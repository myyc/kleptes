import re
import fnmatch

import pandas as pd


class SearchableDataFrame(pd.DataFrame):
    """A DataFrame that implements a (pretty shit, performance-wise)
    search method via __call__"""

    @staticmethod
    def _match(rxp, s):
        if isinstance(rxp, list):
            return sum(
                [1 if re.match(r, s) is not None else 0 for r in rxp]
            ) > 0
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
            raise ValueError("`pattern` must be a string or a list"
                             "of strings.")

        s = pd.Series(False, self.index)

        # hic sunt leones
        for i, r in self.iterrows():
            for c in r.index:
                if self._match(rxp, r[c].lower()):
                    s.loc[i] = True
                    break
        return self[s]
