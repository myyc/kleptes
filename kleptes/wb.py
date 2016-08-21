from itertools import count
import logging


import requests
from redis import StrictRedis


# to be redone, probably.
def wb_get(string="", force=False, params=None, expire=604800):
    base = "http://api.worldbank.org/{}?format=json&per_page=1000&page={}"
    if params is not None and isinstance(params, dict):
        base += "&" + "&".join(["{}={}".format(key, params[key]) for key in params])
    r = StrictRedis()
    key = "WB|{}".format(string)
    if not force and r.exists(key):
        return r.get(key)
    else:
        l = []
        try:
            for p in count(1):
                req = requests.get(base.format(string, p))
                j = req.json()
                req.close()
                pages = j[0]["pages"]
                # log.info("Got page {} of {}{}".format(p, pages, " ..." if p < pages else "!"))
                l.extend(j[1])
                if p >= pages:
                    break
            r.set(key, l)
            if expire is not None:
                r.expire(key, expire)
        except ValueError:
            return None
        return l
