import pandas as pd

from .who import who_dataset, who_dims, who_get
from .oecd import oecd_dataset, oecd_dims, oecd_inds, oecd_md
from .wb import wb_dataset, wb_inds, wb_get
from .eurostat import eus_dataset, eus_inds

import kleptes.goodies
from ._version import __version__

# you really need this.
pd.set_option('max_colwidth', 160)

__all__ = [
    "who_dataset", "who_dims", "who_get",
    "oecd_dataset", "oecd_dims", "oecd_inds",
    "wb_dataset", "wb_inds", "wb_get",
    "eus_dataset", "eus_inds",
    "pd",
    "__version__"
]
