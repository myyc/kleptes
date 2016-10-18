from setuptools import setup
from kleptes._version import __version__


DESC = """
World data mining that sucks a bit less.

Currently available data sets:

* World Bank
* OECD
* WHO

Code and (minimal) documentation `here <https://github.com/myyc/kleptes/>`_.
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
