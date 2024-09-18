#!/usr/bin/env python

from setuptools import setup
from pathlib import Path

setup(
    name = 'PythonYGraph',
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
