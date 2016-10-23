from setuptools import setup
from kleptes._version import __version__


DESC = """
You know that time you wanted to get some world data but it was a dreadful
jungle of bad documentation, requests that make very little sense, ridiculously
complicated data formats (SDMX?), and in the end you just said fuck this
and decided to do something else?

This is an attempt at making world data mining suck a bit less.

Currently available data sets:

* World Bank
* OECD
* WHO
* Eurostat

Source and (minimal) documentation `here <https://github.com/myyc/kleptes/>`_.
"""


setup(
    name="kleptes",
    version=__version__,
    author="myyc",
    description="Goodies to mine world data",
    license="BSD",
    keywords="data mining python pandas who oecd",
    packages=["kleptes"],
    long_description=DESC,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    install_requires=["requests", "pandas", "redis", "bs4"],
)
