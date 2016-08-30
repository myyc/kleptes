import json
import re
import fnmatch

import pandas as pd
import requests
from redis import StrictRedis


def reformat_numbers(d):
    for f in {"a_land_area_kmsq_2012", "d_year"}:
        if f in d:
            n = d[f].replace(",", "")
            d[f] = int(n) if "." not in n else float(n)

def lddf(l, full=False):
    if full:
        d = []
        for r in l:
            if "attr" in r:
                a = {"a_" + d["category"].lower(): d["value"] for d in r["attr"]}
                reformat_numbers(a)
                r.pop("attr")
                d.append(dict(r, **a))
        return pd.DataFrame(d)
    else:
        return pd.DataFrame(l)[["label", "display"]]


def pmatch(l, pattern):
    rxp = re.compile(fnmatch.translate(pattern.lower()))
    return [{"label": k["label"],
             "display": k["display"]} for k in l if
            re.match(rxp, k["label"].lower()) or re.match(rxp, k["display"].lower())]


def parse_ds(ds, names=True):
    l = []

    if names:
        countries = who_countries()
        regions = who_regions()
    else:
        countries, regions = {}, {}

    for x in ds:
        e = {}
        dim = {"d_" + d["category"].lower(): d["code"] for d in x["Dim"]}
        val = {"v_{k}".format(k=k): x["value"][k] for k in {"high", "low", "numeric"} if k in x["value"]}
        reformat_numbers(dim)
        x.pop("Dim")
        x.pop("value")
        e.update(x)
        e.update(dim)
        e.update(val)

        if names:
            if "d_country" in e:
                e["country"] = countries.get(e["d_country"])
            if "d_region" in e:
                e["region"] = regions.get(e["d_region"])

        l.append(e)
    return pd.DataFrame(l)


def who_get(string="", filter_=None, force=False, expire=259200, raw=False):
    """
    Low-level function to get JSON datasets from the WHO database.

    :param string: the thingy to be appended to the url (e.g. 'GHO/blah').
    :param filter_: a filter as per API support (ugh underscore)
    :param force: ignores cached items (but re-caches them)
    :param expire: self-explanatory
    :param raw: returns the JSON dataset as a raw string (useful to debug stuff).
    :return: the requested data set
    """
    filter_ = "&filter={}".format(filter_) if filter_ is not None else ""
    url = "http://apps.who.int/gho/athena/api/{}?format=json{}".format(string, filter_)
    r = StrictRedis()
    key = "WHO|{}|{}".format(string, filter_)

    if not force and r.exists(key):
        t = r.get(key).decode("utf-8")
        if raw:
            return t
        else:
            return json.loads(t)
    else:
        req = requests.get(url)

        # to be removed once they fix the API call result
        t = req.text.replace("Radio band\"\"", "Radio band\"")

        r[key] = t
        if expire is not None:
            r.expire(key, expire)
        if raw:
            return t
        j = json.loads(t)
        return j


def who_dims(name=None, force=False, expire=259200, full=False):
    """
    Get the dimensions from the WHO database. You can do things like `who_dims("*gh*")`.

    :param name: the dimension's name (as mentioned, you can search with `*`)
    :param force: ignores cached items (but re-caches them)
    :param expire: self-explanatory
    :param full: returns the full dataset (by default it only has label and full name).
    :return: the requested data set
    """
    dims = who_get()["dimension"]
    if name is None or name == "":
        return lddf(dims, full)
    elif "*" not in name:
        return lddf(dims, full).query("label == @name or display == @name")
    else:
        return lddf(pmatch(who_get("", force=force, expire=expire)["dimension"], name), full)


def who_dataset(dim=None, name=None, filter_=None, force=False, expire=259200, raw=False, parse=True, full=False):
    """
    Get the dataset "dim/name" from the WHO database. The cool thing is that you can do pattern search on both
    dimension and name, although if you do it on the dimension the name parameter is ignored.

    If you fix a dimension (ideally "GHO" since that's where most of the stuff is) you can do stuff like
    `who_dataset("GHO", "*alcohol*")` and it will search for all the datasets with matching descriptions so no
    need to actually remember the ID's.

    :param dim: the dimension's name
    :param name: the dataset's name
    :param filter_: a filter as per API support
    :param force: ignores cached items (but re-caches them)
    :param expire: self-explanatory
    :param raw: returns the JSON dataset as a raw string (useful to debug stuff).
    :param parse: returns a nice DataFrame as a result (probably what you want unless you're debugging)
    :param full: returns the full dataset (by default it only has label and full name).
    :return: the requested data set
    """
    dims = who_dims(name=dim, force=force, expire=expire)
    if len(dims) > 1:
        return dims
    elif len(dims) == 1:
        dim = dims.iloc[0]["label"]
        if name is None or name == "":
            ds = who_get("{dim}/".format(dim=dim), force=force, expire=expire)["dimension"][0]["code"]
        elif "*" in name:
            ds = pmatch(who_get("{dim}/".format(dim=dim), force=force, expire=expire)["dimension"][0]["code"], name)
        else:
            # exact match
            ds = who_get("{dim}/{name}/".format(dim=dim, name=name),
                         filter_=filter_, force=force, expire=expire, raw=raw)
            return parse_ds(ds["fact"]) if parse and not raw else ds
        return lddf(ds, full=full) if not raw else ds


# two handy shortcuts
def who_countries():
    return {d["label"]: d["display"] for d in who_dataset("COUNTRY", raw=True)}


def who_regions():
    return {d["label"]: d["display"] for d in who_dataset("REGION", raw=True)}
