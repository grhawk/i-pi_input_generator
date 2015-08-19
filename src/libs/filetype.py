#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# Project:  inputsGen
# FileName: filetype
# Creation: Jun 8, 2015
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

import re

# Try determining the version from git:
try:
    import subprocess
    git_v = subprocess.check_output(['git', 'describe'],
                                    stderr=subprocess.DEVNULL)
except subprocess.CalledProcessError:
    git_v = 'Not Yet Tagged!'


__author__ = 'Riccardo Petraglia'
__credits__ = ['Riccardo Petraglia']
__updated__ = "2015-08-19"
__license__ = 'GPLv2'
__version__ = git_v
__maintainer__ = 'Riccardo Petraglia'
__email__ = 'riccardo.petraglia@gmail.com'
__status__ = 'development'


class FileType(object):
    def __init__(self):
        pass

    @classmethod
    def is_type(self, string):
        """Passing the banner string of a structure file return the extension.

        This function helps in determining to which format the given structure
        corresponds. Returns None if no correspondence is found.

        """
        if BannerLines().xyz.match(string): return 'xyz'
        elif BannerLines().gen.match(string): return 'gen'
        else: return 'None'


class BannerLines(object):

    xyz = \
        re.compile(r'^\s*\d+\s*$')  # correspond to an integer
    gen = \
        re.compile(r'^\s*\d+\s+[CcSsFf]\s*$')  # correspond to a gen file
    vector = \
        re.compile(r'\s*[-+]?\d+\.?\d*\s*')  # Just a vector

    def __init__(self):
        pass
