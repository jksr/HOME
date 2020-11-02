#!/usr/bin/env python

from setuptools import setup,find_packages
from pathlib import Path
import sys
import site
import glob

site_dir = site.getsitepackages()[0]


data_files = list(Path("saved_model").rglob("*.*")) + list(Path("training_data").rglob("*.*"))
data_files = [ (site_dir+'/HOME/'+str(x.parent),[str(x)]) for x in data_files]
#print(data_files)

#for x in data_files:
#	print(x)
#hahaha

package_data = []
for i in range(10):
	package_data += glob.glob('*/'*i+'*.npy')+glob.glob('*/'*i+'*.npy')
#print package_data

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
    #include_package_data=True,
    
    #scripts = ["scripts/HOME-pairwise","scripts/HOME-timeseries"],
    packages=find_packages(),
    #packages = ['HOME','HOME/saved_model','HOME/training_data'],
    #packages = ['HOME'],
    #package_data={'': ['*.npy','**/*.npy','*.txt','**/*.txt']},
    package_data={'': ['*.npy','*.txt','*.R']},
    #package_data={'': package_data},
    #data_files=[('saved_model',['saved_model']),('training_data',['training_data'])],
    data_files=data_files,
    entry_points={
        'console_scripts': ['HOME-pairwise=HOME.home_pairwise:real_main',
                            #'HOME-timeseries=scripts.HOME-timeseries:real_main',
                            'HOME-timeseries=HOME.home_timeseries:real_main'
							],
    }
)
