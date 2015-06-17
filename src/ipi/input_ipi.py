#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# Project:  inputsGen
# FileName: input_ipi
# Creation: Jun 9, 2015
#

"""This module take care of the ipi input.

This module provide a default set of keywords and values for the ipi file.
There is some method helping in changing some of the default values such as
temperature, time_step etc.

"""
import xml.etree.ElementTree as etree
import sys

# Try determining the version from git:
try:
    import subprocess
    git_v = subprocess.check_output(['git', 'describe'])
except subprocess.CalledProcessError:
    git_v = 'Not Yet Tagged!'


__author__ = 'Riccardo Petraglia'
__credits__ = ['Riccardo Petraglia']
__updated__ = "2015-06-17"
__license__ = 'GPLv2'
__version__ = git_v
__maintainer__ = 'Riccardo Petraglia'
__email__ = 'riccardo.petraglia@gmail.com'
__status__ = 'development'


class InputTemplate(object):
    """Contains a default version for the ipi input file.

    Only the tags whose value is in CAPITALS can be actually changed by
    the _set method. All the rest of the file will be printed as such.

    If you want to be able to easily modify more tags you can add the tag
    address and a nickname in the self.index dictionary. Consider that the
    address has to start with a . and that each grandparants of the tag has me
    separeted by a '/' symbol.

    You are also allowed to modify directly the input if you require a completly
    different system.

    """
    def __init__(self):
        self.input_template = """<simulation verbosity='medium' mode='md'>
  <total_steps> NSTEPS </total_steps>
  <ffsocket mode="inet" name='dftbuff'>
    <address> ADDRESS </address>
    <port> PORT </port>
    <slots> NUMBEROFSLOTS </slots>
    <timeout> TIMEOUT </timeout>
  </ffsocket>
  <output>
    <properties filename='md' stride='10' flush='10'>
     [step, time{picosecond}, conserved{kilocal/mol}, temperature{kelvin},
     potential{kilocal/mol}, kinetic_md{kilocal/mol}]
    </properties>
    <properties filename='xyz.md' stride='50' flush='10'>
     [step, time{picosecond}, conserved{kilocal/mol}, temperature{kelvin},
     potential{kilocal/mol}, kinetic_md{kilocal/mol}]
    </properties>
    <trajectory filename='pos' stride='50' format='xyz' flush='1'>
        positions{angstrom}
    </trajectory>
    <checkpoint filename='checkpoint'
    stride='1000' overwrite='True' flush='1' />
  </output>
  <system>
    <initialize nbeads='1'>
      <cell mode='abc' units='angstrom'>
    [100, 100, 100]
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
            xyzfile='./system/initialize/file',
            initial_temperature='./system/initialize/velocities',
            temperature='./system/ensemble/temperature',
            timestep='./system/ensemble/timestep',
            nstep='./total_steps',
        )

    def _set(self, key, value):
        """Change the value of the tag in the ipi-input.

        Since the way to find a tag in an xml environment is not straightforward
        and error-prone. I am using this method to check that everything is fine
        while changing the value.

        Args:
            key: the tag object whose value must change
            value: the new value for the key tag object

        Note:
            The value has to be an integer and there have to be only one tag
            with that address otherwise exception will be raised.

        """
        print(self.index[key])
        tags = self.input_xml.findall(self.index[key])
        if len(tags) > 1:
            print('Troppi tag con lo stesso nome')
            exit()
        if not isinstance(value, str):
            print('Value is not str')
            exit()
        try:
            tags[0].text = value
        except IndexError:
            sys.stderr.write('Problems with tags: {} with value: {}\n'.format(
                self.index[key], value))
            raise(IndexError)

    def _add(self, parents, tagname):
        """Add a new tag under a parents tag.

        This method is not yet implemented but will be soon... probably ;)

        """
        raise(NotImplementedError(
            'The _add method is not yet implemented... sorry'))

    def _del(self, tagname):
        """Delete a tag from the input_xml tree.

        This method is not yet implemented but will be soon... maybe ;)

        """
        raise(NotImplementedError(
            'The _del method is not yet implemented... too bad!'))


class InputIpi(InputTemplate):
    """To generate an (hopfully) working ipi input.

    This class is the one that has to be actually used to generate the input
    file. It inherits the template file as an xml object from InputTemplate.
    Provide several public method to modify the template object.

    The self._options dictionary will provide all the input parameter that need
    to be changed in the xml. There are method to manage the _options
    dictionary.

    """
    def __init__(self):
        super().__init__()
        self._options = dict(
            rem='no'
        )

    def set(self, key, value):
        """Set (add/edit) value in the _options dictionary in a safe way.

        Args:
            key: name of the property
            value: new value for the key property

        """
        self._options[key] = value

    def _set_rem(self):
        """Take of care of setting everything if you want to run a rem.

        When running a rem there are few things that needs to be done:
        determining the temperature of each replica and add a few tags in the
        xml template. This method takes care of all of those things.

        Todo:
            This method should use the _add method of the template class...

        """
        rem = self._options.pop('rem')
        if rem.lower() == 'yes':
            try:
                maxtemp = self._options.pop('Tmax')
                mintemp = self._options.pop('Tmin')
                nreps = self._options.pop('nrep')
                rstride = self._options.pop('rstride')
            except KeyError:
                raise(MissingKeywordError(
                    'You miss some REM keyword'))

            temp_list = self._compute_rem_temperature(maxtemp, mintemp, nreps)

            rem = etree.SubElement(self.input_xml, 'paratemp')
            rtemp = etree.SubElement(rem, 'temp_list')
            stride = etree.SubElement(rem, 'stride')
            self.input_xml.set('mode', 'paratemp')
            rtemp.set('units', 'kelvin')
            rtemp_list = ', '.join([str(x) for x in temp_list])
            rtemp.text = '[' + rtemp_list + ']'
            stride.text = ' {:5d} '.format(rstride)

    def _compute_rem_temperature(self, maxtemp, mintemp, nreps):
        """Estimates the best temperature for the replica.

        This subroutine uses the RemTemperatures code to estimates the best
        temperature to be used in a given temperature range and a given number
        of replicas.

        Args:
            maxtemp: temperature of the highest replica
            mintemp: temperature of the lowest replica
            nreps: number of replicas

        Todo: implement something serius... :)
        """
        temp_list = [300.0, 513.00, 1500.14]
        return temp_list

    def indent(self, elem, level=0):
        """This method has been copied from internet to prettify the xml output.

        Args:
            elem: the xml object to be prettified
            level: ...bo... :)
        """
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
        """Create the final input and return it as a string.

        """
        print(self._options)
        if 'rem' in self._options:
                self._set_rem()

        for k, v in self._options.items():
            sys.stderr.write('Setting: {:50s} -> {:50s}\n'.format(k, str(v)))
            if k not in self.index.keys():
                if k == 'mode':
                    pass
                elif k == 'isUnix':
                    if v:
                        self.input_xml.findall('./ffsocket')[0].set('mode', 'unix')
                    else:
                        self.input_xml.findall('./ffsoket')[0].set('mode', 'inet')
                elif k == 'title':
                    continue
                else:
                    raise(IndexError(
                        'Keyword: {} not found in the index'.format(k)))
                    sys.exit()
            else:
                self._set(k, str(v))
            self.indent(self.input_xml)
        return etree.tostring(self.input_xml, method='xml', encoding='us-ascii')


class MissingKeywordError(Exception):
    """This exception is used when keyword are inconsistent.

    """
    def __init__(self, msg):
        sys.stderr.write(msg)
        sys.exit()

if __name__ == '__main__':
    test = InputIpi()
    test.set('rem', 'yes')
    test.set('temperature', 300)
    test.create_input()
