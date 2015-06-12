#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# Project:  inputsGen
# FileName: input_ipi
# Creation: Jun 9, 2015
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

import xml.etree.ElementTree as etree
from input_template import InputTemplate
import sys

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


class InputIpi(InputTemplate):
    def __init__(self):
        super().__init__()
        self.options = dict(
            rem='no'
        )
        self.prop_dict = {}

    def set(self, prop, val):
        self.options[prop] = val

    def _set_rem(self):
        rem = self.options.pop('rem')
        assert(rem.lower() == 'yes')
#        maxtemp = self.options.pop('maxtemperature')
#        mintemp = self.options.pop('mintemperature')
#        nreps = self.options.pop('number_of_replica')
#        rstride = self.options.pop('rem_stride')
        maxtemp = 100; mintemp = 100; nreps = 50; rstride = 10
        self._rem_input(maxtemp, mintemp, nreps, rstride)

    def _rem_input(self, maxtemp, mintemp, nreps, rstride):
        temp_list = [300.0, 513.00, 1500.14]
        rem = etree.SubElement(self.input_xml, 'paratemp')
        rtemp = etree.SubElement(rem, 'temp_list')
        stride = etree.SubElement(rem, 'stride')
        rtemp.set('units', 'kelvin')
        print(temp_list)
        rtemp_list = ', '.join([str(x) for x in temp_list])
        rtemp.text = '[' + rtemp_list + ']'
        stride.text = ' {:5d} '.format(50)

    def indent(self, elem, level=0):
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i


    def create_input(self):
        if 'rem' in self.options and self.options['rem'] == 'yes':
            self._set_rem()
            # del(self.options['maxtemperature'])
            # del(self.options['mintemperature'])
            # del(self.options['number_of_replica'])
            print('Using REM')
        for k, v in self.options.items():
            if k not in self.index.keys():
                print('Problem', k)
                sys.exit()
            print(k, v)
            self._set(k, str(v))

    def _print(self):
        self.indent(self.input_xml)
        etree.dump(self.input_xml)


print(dict)


if __name__ == '__main__':
    test = InputIpi()
    test.set('rem', 'yes')
    test.set('temperature', 300)
    test.create_input()
    test._print()
