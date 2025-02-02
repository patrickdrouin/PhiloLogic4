#!/usr/bin/env python3
from distutils.core import setup

setup(
    name="philologic",
    version="4.6",
    author="The ARTFL Project",
    author_email="artfl@artfl.uchicago.edu",
    packages=["philologic", "philologic.runtime", "philologic.utils", "philologic.runtime.reports", "philologic.loadtime"],
    scripts=["scripts/philoload4"],
    install_requires=["lxml", "python-levenshtein", "natsort", "multiprocess"],
)
