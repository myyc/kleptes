import json
from redis import StrictRedis
import itertools
import pandas as pd
import requests

from .utils import SearchableDataFrame

BASE_URL = "http://api.worldbank.org"


def _wb_url(x, key):
    return "{b}/{k}{c}format=json&per_page=1000&page={x}".format(
        b=BASE_URL, c="&" if "?" in key else "?", k=key,
        x=x)


def wb_get(key, expire=259200, force=False, raw=False):
    """
    Similar to `who_get`, only the things you might get here are more
    complicated. Handles nicely outputs coming from the higher level functions
    below (`wb_inds` and `wb_dataset`), even when they're empty or invalid.

    No guarantees for anything else.

    It might be worth creating ad hoc data types to optimise search.
    """

    r = StrictRedis()

    rkey = "WB|{}".format(key)

    if rkey in r:
        if force:
            del r[rkey]
        else:
            return json.loads(r[key].decode("utf-8"))

    l = []

    dc = False
    n = None

    for i in itertools.count(1):
        req = requests.get(_wb_url(i, key))

        j = req.json()

        if type(j) is list and len(j) == 2:
            if "page" not in j[0]:
                raise ValueError(
                    "Field 'page' not found. (got {})".format(j[0]))
            n = n or int(j[0]["pages"])
            v = j[1]
        elif type(j) is dict and "datacatalog" in j:
            if "page" not in j:
                raise ValueError("Field 'page' not found. (got {})".format(j))
            n = n or int(j["pages"])
            v = j["datacatalog"]
            dc = True
        else:
            raise ValueError(
                "Not sure how to handle the response: {}".format(j))

        v = v or []

        for d in v:
            if not dc and not raw:
                e = {}
                for k in d:
                    if type(d[k]) is dict and "id" in d[k] and "value" in d[k]:
                        e["{}_id".format(k)] = d[k]["id"]
                        e[k] = d[k]["value"]
                    elif type(d[k]) is list:
                        if d[k] and "id" in d[k][0] and "value" in d[k][0]:
                            e[k] = ", ".join(
                                [v["value"].strip() for v in d[k]])
                        else:
                            e[k] = ""
                    else:
                        e[k] = d[k]
            else:
                e = d
            l.append(e)

        if i == n or n == 0:
            break

    r[rkey] = json.dumps(l)
    r.expire(rkey, expire)

    return l


def wb_inds(k=None, expire=259200, force=False, raw=False):
    """This function takes ages. Needs some thought."""
    ds = wb_get("indicators", force=force, expire=expire)
    return ds if raw else SearchableDataFrame(ds)(k)


# todo: add parameters like mrv etc.
def wb_dataset(ind, countries="all", d1=1960, d2=2016, frequency="Y",
               expire=259200, force=False, raw=False):
    if countries != "all":
        countries = ";".join(countries)

    params = "date={d1}:{d2}&frequency={f}".format(d1=d1, d2=d2, f=frequency)
    k = "countries/{c}/indicators/{ind}?{params}".format(c=countries,
                                                         ind=ind,
                                                         params=params)
    ds = wb_get(k, force=force, expire=expire)
    return ds if raw else pd.DataFrame(ds)
