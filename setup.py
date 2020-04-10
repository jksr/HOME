#!/usr/bin/env python

from setuptools import setup



setup(
    name = 'HOME',
    version = '1.0.0',
    description="HOME: Histogram Of MEthylation",
    author = 'akanksha srivastava',
    install_requires = [
        'numpy',
        'pandas',
        'scipy',
        'scikit-learn',
        'statsmodels',
    ],
    author_email = 'akanksha.srivastava@research.uwa.edu.au',
    include_package_data=True,
    
    scripts = ["scripts/HOME-pairwise","scripts/HOME-timeseries"],
    packages = ['HOME'],
)
