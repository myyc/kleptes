import io

import pendulum
from mnemon import mnd
import requests
import pandas as pd

_cols = {"Date": "dt", "Open": "open", "High": "high", "Low": "low",
         "Close": "close", "Volume": "volume", "Adj Close": "adj_close"}


@mnd(raw=True, expire=7200)
def tg(url):
    return requests.get(url).content


@mnd(expire=3600)
def jg(url):
    return requests.get(url).json()


def yurl(sym, d1, d2):
    return ("http://ichart.yahoo.com/table.csv?s={sym}"
            "&a={m1}&b={d1}&c={y1}"
            "&d={m2}&e={d2}&f={y2}").format(
        sym=sym, m1=d1.month - 1, d1=d1.day, y1=d1.year,
        m2=d2.month - 1, d2=d2.day, y2=d2.year
    )


def _parsedate(d):
    if d is None or type(d) is pendulum.pendulum.Pendulum:
        return d
    elif type(d) is str:
        return pendulum.datetime.parse(d)
    else:
        raise TypeError(type(d))


def _dchunk(d1, d2):
    cs = 100
    d = d2 - d1
    if d.days <= cs:
        return [(d1, d2)]
    else:
        r1 = list(range(0, d.days, cs))
        r2 = list(range(cs - 1, d.days, cs)) + [d.days]
        return [(d1.add(days=i), d1.add(days=k)) for (i, k) in zip(r1, r2)]


def yf_search(q, how="df"):
    j = jg("http://d.yimg.com/aq/autoc?query={}&region=GB&lang=en".format(q))
    if how == "raw":
        return j
    cols = ["type", "symbol", "name", "typeDisp", "exch", "exchDisp"]
    return pd.DataFrame(j["ResultSet"]["Result"], columns=cols)


def yf_get(sym, d1=None, d2=None, days=None):
    if type(sym) == str:
        d1 = _parsedate(d1)
        d2 = _parsedate(d2)
        if d1 is not None and d2 is not None and days is not None:
            raise ValueError("Choose at most two (d1, d2, days)")
        if d2 is None:
            d2 = pendulum.datetime.now()
        if days is None:
            days = 90
        if d1 is None:
            d1 = d2.subtract(days=days)

        l = []
        for (d1, d2) in _dchunk(d1, d2):
            url = yurl(sym, d1, d2)

            csv = tg(url)
            try:
                tmpdf = pd.read_csv(io.BytesIO(csv), encoding="utf-8")
                l.append(tmpdf)
            except:
                pass

        if len(l) == 0:
            return None

        csvdf = pd.concat(l)

        return (
            csvdf.rename(columns=_cols)
                .assign(dt=lambda x: x["dt"].astype("datetime64"))
                .set_index("dt")
                .assign(sym=sym)
                .set_index("sym", append=True).sort_index()
        )
    elif hasattr(sym, "__getitem__") or hasattr(sym, "__iter__"):
        df = None
        for s in sym:
            _df = yf_get(s, d1, d2, days)
            if _df is not None:
                df = _df if df is None else df.append(_df)
        return df
    else:
        raise ValueError("'sym' needs to be a str or an iterable")
