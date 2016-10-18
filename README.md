kleptes
=======

Some world data mining goodness.

* *[WHO](http://who.int/en/)* - pretty good, not super complete, very easy
to browse.
* *[OECD](https://www.oecd.org/)* - a complete nightmare. Takes minutes
to figure out if a dataset has any data.

*Requirements*
--------------

* Python 3
* `pandas`
* Redis (to cache stuff; defaults to localhost, hardcoded)
* `requests`
* `bs4` (used only in one function, don't worry)

It's on PyPI so you can simply `pip3 install kleptes`.

*How do I use this?*
--------------------

It's meant to be used in a Jupyter notebook (or anything interactive,
so a Jupyter notebook).

```python
from kleptes import *   # also imports pandas as pd. you'll thank me

who_dims()
who_dims("*indic*")  # supports unix searching because who the fuck knows regexps?

who_dataset("GHO")                # wow results much stuff
who_dataset("GHO", "*suicide*")   # fewer

who_dataset("GHO", "MH_12").head()   # the thing you were looking for

# same stuff for the OECD
oecd_inds("*quarterly*")   # search among indicators (so much shit there)

oecd_dims("QNA")                      # get the dimension of said indicator
oecd_dims("QNA").subject("*gross*")   # figure out possible values of each field
oecd_dataset("qna",
             country=["italy", "fra", "germany", "norw*"],
             subject=["B1_GE"],
             measure="cqr",
             frequency="Q")  # as many kwargs as the dims.
```

Remember: *everything should be searchable*.

The exposed functions for now are:

* WHO: `who_dataset`, `who_dim` and `who_get` (very low level).
* OECD: `oecd_dataset`, `oecd_dims`, `oecd_ind`

They serve different purposes so despite the name they don't do
exactly the same thing (e.g. `who_dim` and `oecd_dims` do different stuff).

Everything is cached for a while so you won't be flooding the servers
unless you want to.

*What's in a name?*
-------------------

"Kleptes" (*κλέπτης*) is an Ancient Greek word for "thief" (think about
"kleptomania"). Such pretentious much clever very antique.