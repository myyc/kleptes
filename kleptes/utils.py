import re
import fnmatch

import pandas as pd

# three days
EXPIRE = 259200


def get_re(pattern):
    if type(pattern) == str:
        return re.compile(fnmatch.translate(pattern), flags=re.IGNORECASE)
    elif type(pattern) == list:
        return re.compile("|".join(fnmatch.translate(pattern)),
                          flags=re.IGNORECASE)
    else:
        raise ValueError("'pattern' must either be a string or a list "
                         "(or None)")


class SearchableDataFrame(pd.DataFrame):
    """A DataFrame that implements a search method via __call__"""

    def __call__(self, pattern=None, cols=None):
        if pattern is None:
            return self

        p = get_re(pattern)

        if cols not in list(self.columns):
            if cols is None:
                _df = self.select_dtypes(["object"])
            elif type(cols) == list:
                _df = self[cols]
            else:
                raise ValueError("'cols' must be either a 'list', 'None' or "
                                 "the name of a column.")
            s = _df.apply(lambda x: x.str.match(p)).sum(axis=1).astype("bool")
        else:
            s = self[cols].str.match(p)
        return self[s]
