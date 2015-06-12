#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# Project:  inputsGen
# FileName: input_template
# Creation: Jun 10, 2015
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


class InputTemplate(object):
    def __init__(self):
        self.input_template = """<simulation verbosity='medium' mode='md'>
  <total_steps> 6000000 </total_steps>
  <ffsocket mode="inet" name='dftbuff'>
    <address> ADDRESS </address>
    <port> PORT </port>
    <slots> NUMBEROFSLOTS </slots>
    <timeout> TIMEOUT </timeout>
  </ffsocket>
  <output>
    <properties filename='md' stride='10' flush='10'> [step, time{picosecond}, conserved{kilocal/mol}, temperature{kelvin}, potential{kilocal/mol}, kinetic_md{kilocal/mol}] </properties>
    <properties filename='xyz.md' stride='50' flush='10'> [step, time{picosecond}, conserved{kilocal/mol}, temperature{kelvin}, potential{kilocal/mol}, kinetic_md{kilocal/mol}] </properties>
    <trajectory filename='pos' stride='50' format='xyz' flush='1'> positions{angstrom} </trajectory>
    <checkpoint filename='checkpoint' stride='1000' overwrite='True' flush='1' />
  </output>
  <system>
    <initialize nbeads='1'>
      <cell mode='abc' units='angstrom'>
    [1000, 1000, 1000]
      </cell>
      <file mode='xyz' units='angstrom'> XYZFILE </file>
      <velocities mode='thermal' units='kelvin'> INITIALVELOCITY </velocities>
    </initialize>
    <forces>
      <force name='dftb-uff'> dftbuff </force>
    </forces>
    <ensemble mode='nvt'>
      <thermostat mode='gle'>
    <A shape='(7,7)'>
      [   8.191023526179e-5,    8.328506066524e-4,    1.657771834013e-4,    9.736989925341e-5,    2.841803794895e-5,   -3.176846864198e-6,   -2.967010478210e-5,
      -8.389856546341e-5,    2.405526974742e-3,   -1.507872374848e-3,    2.589784240185e-4,    1.516783633362e-4,   -5.958833418565e-5,    4.198422349789e-5,
      7.798710586406e-5,    1.507872374848e-3,    8.569039501219e-4,    6.001000899602e-4,    1.062029383877e-4,    1.093939147968e-4,   -2.661575532976e-4,
      -9.676783161546e-5,   -2.589784240185e-4,   -6.001000899602e-4,    2.680459336535e-6,   -5.214694469742e-6,    4.231304910751e-5,   -2.104894919743e-6,
      -2.841997149166e-5,   -1.516783633362e-4,   -1.062029383877e-4,    5.214694469742e-6,   1.433903506353e-10,   -4.241574212449e-6,    7.910178912362e-6,
      3.333208286893e-6,    5.958833418565e-5,   -1.093939147968e-4,   -4.231304910751e-5,    4.241574212449e-6,    2.385554468441e-9,   -3.139255482869e-6,
      2.967533789056e-5,   -4.198422349789e-5,    2.661575532976e-4,    2.104894919743e-6,   -7.910178912362e-6,    3.139255482869e-6,   2.432567259684e-12
      ]
    </A>
      </thermostat>
      <timestep units='femtosecond'> TIMESTEP </timestep>
      <temperature units='kelvin'> TEMPERATURE </temperature>
    </ensemble>
  </system>
</simulation>
"""
        self.input_xml = etree.fromstring(self.input_template)
        self.index = dict(
            # FFSOCKET
            address='./ffsocket/address',
            port='./ffsocket/port',
            slots='./ffsocket/slots',
            timeout='./ffsocket/timeout',
            # SYSTEM
            xyzfile='./system/initialize/xyzfile',
            init_temperature='./system/initialize/velocities',
            temperature='./system/ensemble/temperature',
            timestep='./system/ensemble/timestep'
        )

    def _set(self, key, value):
        tags = self.input_xml.findall(self.index[key])
        if len(tags) > 1:
            print('Troppi tag con lo stesso nome')
            exit()
        if not isinstance(value, str):
            print('Value is not str')
            exit()
        tags[0].text = value


