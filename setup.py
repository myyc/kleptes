import os
from setuptools import setup

VERSION = "0.2.1"


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="kleptes",
    version=VERSION,
    author="myyc",
    description="Goodies to mine world data",
    license="BSD",
    keywords="data mining python jupyter who",
    packages=["kleptes"],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    install_requires=["requests", "pandas", "redis", "bs4"],
)
