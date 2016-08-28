kleptes
=======

Some world data mining goodness.

* WHO
* OECD

*Requirements*
--------------

* Pandas
* Redis (defaults to localhost, hardcoded)
* requests
* bs4

*How do I use this?*
--------------------

It's meant to be used in a Jupyter notebook (or anything interactive).

```python
from kleptes import *   # also imports pandas as pd. you'll thank me

who_dims()
who_dims("*indic*")  # supports unix searching because who the fuck knows regexps?

who_dataset("GHO")                # wow results much stuff
who_dataset("GHO", "*suicide*")   # fewer

who_dataset("GHO", "MH_12").head()   # the thing you were looking for

# same stuff for the OECD
oecd_ind("*quarterly*")
oecd_dims("QNA")
oecd_dims("QNA").subject("*gross*")
oecd_dataset("qna",
             country=["italy", "fra", "germany", "norw*"],
             subject=["P61", "B1_GE"],
             measure="cqr",
             frequency="Q")  # as many kwargs as the dims.
```

The exposed functions for now are:

* WHO: `who_dataset`, `who_dim` and `who_get` (very low level).
* OECD: `oecd_dataset`, `oecd_dims`, `oecd_ind`, `oecd_md`

They serve different purposes so despite the name they don't do
exactly the same thing (e.g. dimensions have different meanings).

Everything is cached for a while so you won't be flooding the servers
unless you want to.

*What's in a name?*
-------------------

"Kleptes" (*κλέπτης*) is an Ancient Greek word for "thief" (think about
"kleptomania"). Such pretentious much clever very antique.