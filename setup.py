import os
from setuptools import setup

VERSION = "0.1.dev666"


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="kleptes",
    version=VERSION,
    author="myyc",
    description="Misc utils to mine some data",
    license="LGPL",
    keywords="data mining python jupyter who",
    packages=["kleptes"],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    install_requires=["requests", "pandas", "redis"],
)
