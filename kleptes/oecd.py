import re
import fnmatch
import json

import requests
from bs4 import BeautifulSoup
from redis import StrictRedis
import pandas as pd

BASE_URL = "http://stats.oecd.org/sdmx-json"


def get_index(ds):
    """Converts the index to a DatetimeIndex"""
    v = [pd.Period(k["id"]).start_time for k in ds["structure"]["dimensions"]["observation"][0]["values"]]
    idx = pd.DatetimeIndex(v)
    idx.name = "d"
    return idx


def pk(ds, ks):
    """Converts things like 0:2:0:1 into a dictionary matching what the numbers mean."""
    a = [int(i) for i in ks.split(":")]
    key = ds["structure"]["dimensions"]["series"]
    n = [k["name"].lower() for k in key]

    # this should be configurable. right now it's just 'id': 'value', could be 'name': 'value', etc.
    l = [[v["id"] for v in k["values"]] for k in key]

    return {n[i]: l[i][a[i]] for i in range(len(a))}


def parseds(ds):
    if len(ds["dataSets"]) > 1:
        print(len(ds["dataSets"]))
    s = ds["dataSets"][0]["series"]

    df = None

    for k in s:
        kt = pk(ds, k)

        o = s[k]["observations"]
        l = {int(i): o[i][0] for i in o}
        idx = get_index(ds)
        _df = (
            pd.Series(l).to_frame("value").reindex(range(0, len(idx)))
                .assign(dt=idx).assign(**kt).set_index("dt")
        )
        df = _df if df is None else pd.concat((df, _df))

    return df


class SearchableDataFrame(pd.DataFrame):
    """A DataFrame that implements a (pretty shit, performance-wise) search method via __call__"""

    @staticmethod
    def _match(rxp, s):
        if isinstance(rxp, list):
            return sum([1 if re.match(r, s) is not None else 0 for r in rxp]) > 0
        else:
            return re.match(rxp, s)

    def __call__(self, pattern=None):
        if pattern is None:
            return self
        if isinstance(pattern, str):
            rxp = re.compile(fnmatch.translate(pattern.lower()))
        elif isinstance(pattern, list):
            rxp = [re.compile(fnmatch.translate(p.lower())) for p in pattern]
        else:
            raise ValueError("`pattern` must be a string or a list of strings.")

        s = pd.Series(False, self.index)

        # hic sunt leones
        for i, r in self.iterrows():
            for c in r.index:
                if self._match(rxp, r[c].lower()):
                    s.loc[i] = True
                    break
        return self[s]


class OECDims:
    def __iter__(self):
        return self._keys.__iter__()

    def __getitem__(self, i):
        return self._d[i]

    def __repr__(self):
        return "OECDims(\"{}\", {})".format(self._name, self._keys)

    def __call__(self, pattern=None):
        df = None
        for k in self:
            _df = self._d[k](pattern).assign(dim=k)
            df = _df if df is None else pd.concat([df, _df])
        return df[["dim", "id", "name"]]

    def __init__(self, md, name=""):
        self._keys = []
        self._d = {}
        self._name = "\"\"" if len(name) == 0 else name
        for x in md:
            if "role" in x and x["role"] == "TIME_PERIOD":
                continue
            attr = x["name"].lower()
            self._keys.append(attr)
            self._d[attr] = SearchableDataFrame(x["values"], columns=["id", "name"])
            self.__setattr__(attr, self._d[attr])


def oecd_inds(pattern=None, force=False, expire=259200, df=True):
    """No way to get the indicators without scraping."""
    key = "OECD|inds"
    r = StrictRedis()
    if key in r and not force:
        l = json.loads(r[key].decode("utf-8"))
    else:
        t = requests.get(BASE_URL + "/").text
        soup = BeautifulSoup(t, "html.parser")
        l = {i["value"].strip(): i.text.strip() for i in list(soup.find(id="Datasets").children)[2:] if i != "\n"}
        r[key] = json.dumps(l)
        r.expire(key, expire)
    if pattern is not None and pattern != "":
        rxp = re.compile(fnmatch.translate(pattern.lower()))
        l = {k: l[k] for k in l if re.match(rxp, k.lower()) or re.match(rxp, l[k].lower())}
    if df:
        d = [{"id": k, "desc": l[k]} for k in l]
        return pd.DataFrame(d, columns=["id", "desc"])
    else:
        return l


def oecd_md(pattern, force=False, expire=259200):
    idxs = oecd_inds(pattern, df=False)
    if len(idxs) == 0:
        raise ValueError("Empty selection")
    elif len(idxs) > 1:
        raise ValueError("Selection is too wide")

    idx = list(idxs.keys())[0]
    key = "OECD|{}|md".format(idx)

    r = StrictRedis()

    if key not in r or force:
        j = requests.get("{}/metadata/{}".format(BASE_URL, idx)).json()
        r[key] = json.dumps(j)
        r.expire(key, expire)
    else:
        j = json.loads(r[key].decode("utf-8"))

    return j


def oecd_dims(pattern, force=False, expire=259200):
    md = oecd_md(pattern, force, expire)
    name = md["structure"]["name"]
    return OECDims(md["structure"]["dimensions"]["observation"], name)


def oecd_dataset(idx, rawstr=None, force=False, expire=259200, raw=False, **kwargs):
    if rawstr is None:
        if kwargs is None:
            raise ValueError("If `rawstr` is None you need to set kwargs according to the dimension.")
        dims = oecd_dims(idx)

        pmise = lambda x: "+".join(x["id"])

        rawstr = ".".join([pmise(dims[l](kwargs[l])) for l in dims])

    key = "OECD|{}|data".format(rawstr)

    r = StrictRedis()
    if key not in r or force:
        j = requests.get("{}/data/{}/{}/all".format(BASE_URL, idx, rawstr)).json()
        r[key] = json.dumps(j)
        r.expire(key, expire)
    else:
        j = json.loads(r[key].decode("utf-8"))
    if raw:
        return j
    else:
        return parseds(j).assign(ind=idx.upper())
