#!/usr/bin/env python

# Adapted from hgview-1.3.0/setup.py:
# http://www.logilab.org/project/hgview

from distutils.core import setup
from distutils.command.build import build
import os
from os.path import join, splitext

class QtBuild(build):
    def compile_rc(self, qrc_file, py_file=None):
        # Search for pyuic4 in python bin dir, then in the $Path.
        if py_file is None:
            py_file = splitext(qrc_file)[0] + ".py"
        if os.system('pyrcc4 "%s" -o "%s"' % (qrc_file, py_file)) > 0:
            print "Unable to generate python module for resource file", qrc_file
            exit(1)

    def run(self):
        for dirpath, _, filenames in os.walk('pygraph'):
            for filename in filenames:
                if filename.endswith('.qrc'):
                    self.compile_rc(join(dirpath, filename))
        build.run(self)

setup(
		name = 'pygraph',
		version = '0.1',
		description = 'A freely available, lightweight and easy to use ' +
            'visualization client for viewing 1D data files.',
        author = 'David Radice',
        author_email = 'david.radice@aei.mpg.de',
        cmdclass = {'build': QtBuild},
        license = 'GPLv3',
        packages = ['pygraph'],
        package_data = {'pygraph' : ['data/*']},
        requires = ['scidata', 'PyQt', 'PyQwt'],
        scripts = ['./bin/pygraph'],
        url = 'https://bitbucket.org/dradice/scidata'
        )
