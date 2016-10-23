from io import BytesIO
import gzip

import pandas as pd
from redis import StrictRedis
import requests
import numpy as np

from .utils import SearchableDataFrame, EXPIRE


def _eus_proc_tsv(s, key, expire=EXPIRE, force=False):
    """
    This thing is horrific. It's meant to completely reprocess the data
    not just so that it's 'better' for pandas, but also so that it's
    actually readable.

    Datasets are shaped this way:

    ``"pk1,pk2,...,pkn\time"\t"yyyyMmm"\t"yyyyMmm"...``

    So that:

    1. The first field is always a comma-separated primary key (lol)
    2. Years are not part of the primary key, they're columns (lol)

    This function outputs a DataFrame shaped as:

    ``pk1;pk2;...;pkn;time;value``

    with the primary key split accordingly and time as a row index.
    """
    key = "EUS_ds|{}|proc".format(key)
    r = StrictRedis()
    if force:
        if key in r:
            del r[key]

    if key in r:
        return pd.read_csv(BytesIO(r[key]), compression="gzip")

    df = None
    ndf = None
    cols = None

    hl = 0

    l = []

    for row in gzip.open(BytesIO(s)):
        row = row.decode("utf-8")
        ra = row.strip().split("\t")

        # get the "primary key"
        fe = ra[0].split(",")
        del ra[0]

        ra = fe + ra  # the row is the full primary key + the actual row
        if df is None:
            hl = len(fe)

            # of course the fourth element of the primary key is called
            # ``"pkn\time"``.
            ra[hl-1] = ra[hl-1].replace("\\time", "")
            cols = ra

            for i, k in enumerate(ra[hl:]):
                # years contain months as M. replacing to convert YYYYMmm into
                # YYYY-mm
                ra[hl + i] = k.strip().replace("M", "-")

            df = pd.DataFrame([], columns=cols)
            for k in df.columns[hl:]:
                df[k] = df[k].astype("float")
        else:
            for i, k in enumerate(ra):
                if i >= hl:
                    # of course ":" means NA
                    if ":" in k:
                        ra[i] = np.nan
                    else:
                        # sometimes floats have notes. (e.g. "195.2 f").
                        spi = k.strip().find(" ")
                        if spi > 0:
                            ra[i] = float(k.strip()[:spi])
                        else:
                            ra[i] = float(k)
            l.append(ra)
        # do it in bulks
        if len(l) >= 500:
            # the actual reshaping + type conversion
            _df = (
                df.append(pd.DataFrame(l, columns=cols))
                .set_index(cols[:hl]).stack().astype("float")
            )
            if ndf is None:
                ndf = _df
            else:
                ndf = ndf.append(_df)
            l = []

    # parse the rest. kind of c-esque, must find a better way
    if len(l) > 0:
        _df = (
            df.append(pd.DataFrame(l, columns=cols))
            .set_index(cols[:hl]).stack().astype("float")
        )
        ndf = ndf.append(_df) if ndf is not None else _df

    ndf.index.names = list(ndf.index.names[:hl]) + ["time"]
    ndf = ndf.to_frame("value").reset_index()

    r[key] = gzip.compress(ndf.to_csv(index=None).encode("utf-8"))
    r.expire(key, expire)

    return ndf


def _eus_get(key, url, expire=EXPIRE, force=False):
    r = StrictRedis()

    if force:
        del r[key]
    if key in r:
        return r[key]
    else:
        t = requests.get(url).content
        r[key] = t
        r.expire(key, expire)
        return r[key]


def eus_inds(k=None, expire=EXPIRE, force=False):
    """
    Same syntax as all the others. Returns a ``SearchableDataFrame``.

    :param k: search key (only in the title column)
    :param expire: same as usual
    :param force: same as usual
    :return: a ``SearchableDataFrame`` with the indicators and other stuff.
    """
    key = "EUS_inds"
    url = ("http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/"
           "BulkDownloadListing?file=table_of_contents_en.txt")
    b = _eus_get(key, url, expire=expire, force=force)

    eudf = SearchableDataFrame(pd.read_csv(BytesIO(b), sep="\t"))
    return eudf(k, cols="title")


def eus_dataset(ds=None, expire=EXPIRE, force=False):
    """
    This thing returns a barely recognisable version of the original dataset;
    much more efficient for pandas manipulation.

    It downloads stuff from the bulk download service instead of the API
    because the API isn't searchable in any published way.

    :param ds: exact match this time
    :param expire: same as usual
    :param force: same as usual
    :return: a ``SearchableDataFrame`` with the indicators and other stuff.
    """
    cds = set(eus_inds()["code"])
    if ds not in cds:
        raise KeyError("Code '{}' not found".format(ds))

    key = "EUS_ds|{}".format(ds)
    url = ("http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/"
           "BulkDownloadListing?sort=1&"
           "file=data%2F{code}.tsv.gz").format(code=ds)

    df = _eus_proc_tsv(_eus_get(key, url, expire=expire, force=force), key=key,
                       expire=expire, force=force)
    return df
