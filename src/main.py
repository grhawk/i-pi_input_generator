#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# Project:  inputsGen
# FileName: main
# Creation: Jun 12, 2015
#

"""Example Google style docstrings.

This module demonstrates documentation as specified by the `Google Python
Style Guide`_. Docstrings may extend over multiple lines. Sections are created
with a section header and a colon followed by a block of indented text.

Example:
  Examples can be given using either the ``Example`` or ``Examples``
  sections. Sections support any reStructuredText formatting, including
  literal blocks::

      $ python example_google.py

Section breaks are created by simply resuming unindented text. Section breaks
are also implicitly created anytime a new section starts.

Attributes:
  module_level_variable (int): Module level variables may be documented in
    either the ``Attributes`` section of the module docstring, or in an
    inline docstring immediately following the variable.

    Either form is acceptable, but the two should not be mixed. Choose
    one convention to document module level variables and be consistent
    with it.

.. _Google Python Style Guide:
   http://google-styleguide.googlecode.com/svn/trunk/pyguide.html

"""

import argparse


# Try determining the version from git:
try:
    import subprocess
    git_v = subprocess.check_output(['git', 'describe'])
except subprocess.CalledProcessError:
    git_v = 'Not Yet Tagged!'


__author__ = 'Riccardo Petraglia'
__credits__ = ['Riccardo Petraglia']
__updated__ = "2015-06-12"
__license__ = 'GPLv2'
__version__ = git_v
__maintainer__ = 'Riccardo Petraglia'
__email__ = 'riccardo.petraglia@gmail.com'
__status__ = 'development'


def main():
    pass

def _parser():
    parser = argparse.ArgumentParser(
        description='Helps in build REM@DFTB input files.')

    parser.add_argument('Tmin',
                        action='store',
                        type=float,
                        help='Smallest REM temperature')

    parser.add_argument('Tmax',
                        action='store',
                        type=float,
                        help='Highest REM temperature')

    parser.add_argument('N',
                        action='store',
                        type=int,
                        help='Number of replicas')

    parser.add_argument('--debug',
                        action='store_true',
                        dest='debug_flag',
                        default=False,
                        help='be more verbose')


    return parser.parse_args()

if __name__ == '__main__':
    main()
