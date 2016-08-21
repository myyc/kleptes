kleptes
=======

Some world data mining goodness.

*Requirements*
--------------

* Pandas
* Redis (defaults to localhost, hardcoded)
* requests

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
```

The only exposed functions for now are `who_dataset`, `who_dim` and `who_get` (very low level).

Everything is cached for a while so you won't be flooding the servers unless you want to.

*What's in a name?*
-------------------

"Kleptes" (*κλέπτης*) is an Ancient Greek word for "thief" (think about "kleptomania"). Such pretentious
much clever very antique.