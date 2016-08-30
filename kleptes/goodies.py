import uuid

import pandas as pd


def _sbs(df, ascending=True, copy=True):
    """
    Sometimes you want a stacked bar plot and have the bars sorted by their sum: this is the case for labelled bar
    plots, which are stacked plots where only one bar has non-zero height, e.g. say you have a metric by country, each
    of which is labelled by a region/continent and you want to colour the bars by region/continent. Simply call
    df.sbs() on your multicolumn dataframe and you're done. If you only have one column this function will have no
    effect.

    :param df: a DataFrame (it must have one index only and, ideally, more columns)
    :param ascending: sort in ascending order (default: False)
    :param copy: get a copy or sort in-place (default: True)
    :return: your sorted DataFrame
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("The argument must be a DataFrame")
    _df = df.copy() if copy else df
    c = uuid.uuid4()
    _df[c] = _df.sum(axis=1)
    _df = _df.sort_values(c, ascending=ascending)
    del _df[c]
    return _df


pd.DataFrame.sbs = _sbs
