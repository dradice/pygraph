#!/usr/bin/env python

# Adapted from hgview-1.3.0/setup.py:
# http://www.logilab.org/project/hgview

from setuptools import setup
import os
from os.path import join, splitext

setup(
    name = 'pygraph',
    version = '1.1',
    description = 'A freely available, lightweight and easy to use ' +
        'visualization client for viewing 1D data files.',
    author = 'David Radice',
    author_email = 'david.radice@psu.edu',
    license = 'GPLv3',
    packages = ['pygraph', 'scidata', 'scidata/carpet'],
    package_data = {'pygraph' : ['data/*']},
    install_requires = ['pyqt5', 'pythonqwt', 'numpy', 'h5py'],
    scripts = ['./bin/pygraph'],
    url = 'https://bitbucket.org/dradice/pygraph'
)
