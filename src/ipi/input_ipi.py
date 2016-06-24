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
import scipy.optimize as optim
import numpy as np

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


class InputTemplate(object):
    """Contains a default version for the ipi input file.

    Only the tags whose value is in CAPITALS can be actually changed by
    the _set_value method. All the rest of the file will be printed as such.

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
    <properties filename='md' stride='50' flush='10'>
     [step, time{picosecond}, conserved{kilocal/mol}, temperature{kelvin},
     potential{kilocal/mol}, kinetic_md{kilocal/mol}, bias_potential{kilocal/mol}, ensemble_logweight, hamiltonian_w]
    </properties>
    <trajectory filename='pos' stride='50' format='xyz' flush='1'>
        positions{angstrom}
    </trajectory>
    <checkpoint filename='checkpoint'
    stride='1000' overwrite='True' />
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
            system='./system',
        )

    def _tag_checkout(self, tag_key):
        tags = self.input_xml.findall(self.index[tag_key])

        # when a bias is present following tags appear twice
        c1 = tag_key == 'port'
        c2 = tag_key == 'slots'
        c3 = tag_key == 'address'
        c4 = tag_key == 'timeout'
        c5 = len(self.input_xml.findall('./system/bias')) > 0
        if c5 and (c1 or c2 or c3 or c4):
            allowed_tags = 2
        else:
            allowed_tags = 1

        if len(tags) > allowed_tags:
            print('Troppi tag con lo stesso nome')
            print(tags[0])
            exit()
        if len(tags) < 1:
            print('Tag {} associato alla chiave {} non esistente\n'.format(
                self.index[tag_key]), tag_key)
            exit()
        return tags[0]

    def _value_checkout(self, value):
        if not isinstance(value, str):
            estr = 'Only str can be managed by the xml engine - value:{}'
            raise TypeError(estr.format(value))
        return value

    def _set_value(self, tag_key, value):
        """Change the value of the tag in the ipi-input.

        Since the way to find a tag in an xml environment is not straightforward
        and error-prone. I am using this method to check that everything is fine
        while changing the value.

        Args:
            tag_key: the tag object whose value must change
            value: the new value for the tag_key tag object

        Note:
            The value has to be an integer and there have to be only one tag
            with that address otherwise exception will be raised.

        """
        self._value_checkout(value)
        tag = self._tag_checkout(tag_key)
        try:
            tag.text = value
        except IndexError:
            sys.stderr.write('Problems with tags: {} with value: {}\n'.format(
                tag_key, value))
            raise(IndexError)

    def _set_attrib(self, tag_key, key, value):
        self._value_checkout(value)
        self._value_checkout(key)
        tag = self._tag_checkout(tag_key)
        try:
            tag.set(key, value)
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
                steep = self._options.pop('steep')
            except KeyError:
                raise(MissingKeywordError(
                    'You miss some REM keyword'))

            temp_list = self._compute_rem_temperature(maxtemp, mintemp, nreps, steep)

            rem = etree.SubElement(self.input_xml, 'paratemp')
            rtemp = etree.SubElement(rem, 'temp_list')
            stride = etree.SubElement(rem, 'stride')
            self.input_xml.set('mode', 'paratemp')
            rtemp.set('units', 'kelvin')
            rtemp_list = ', '.join([str(x) for x in temp_list])
            print('TEMPLIST:' + '[' + rtemp_list + ']')
            rtemp.text = '[' + rtemp_list + ']'
            stride.text = ' {:5d} '.format(rstride)
            self._set_attrib('system', 'copies', str(nreps))
            if self._options['bias']:
                bias_list = []
                for x in temp_list:
                    # if x < 1800 and x > 1500:
                    #     bias_list.append(0.5)
                    # elif x > 1500:
                    #     bias_list.append(1)
                    # else:
                    #     bias_list.append(0)
                    bias_list.append(1)
                rbias = etree.SubElement(rem, 'bias_list')
                rbias_list = ', '.join([str(x) for x in bias_list])
                rbias.text = '[' + rbias_list + ']'

    def _set_bias(self):
        # Add bias to the system
        system = self.input_xml.findall('./system')[0]
        bias = etree.SubElement(system, 'bias')
        bias_force = etree.SubElement(bias, 'force')
        bias_force.text = 'plumed_bias'

        # Add force to the ffsocket
        ffsocket = etree.SubElement(self.input_xml, 'ffsocket')
        ffsocket.set('name', 'plumed_bias')
        address = etree.SubElement(ffsocket, 'address')
        port= etree.SubElement(ffsocket, 'port')
        slots = etree.SubElement(ffsocket, 'slots')
        timeout = etree.SubElement(ffsocket, 'timeout')
        port.text = str(self._options['port_bias'])
        address.text = str(self._options['address'])
        slots.text = str(self._options['slots'])
        timeout.text = str(self._options['timeout'])
        
        self._options.pop('port_bias')
        
    def _compute_rem_temperature(self, maxtemp, mintemp, nreps, steep):
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

        temp_list = remTempEstimator(mintemp, maxtemp, nreps, steep).t_list
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
        if 'rem' in self._options:
            self._set_rem()
        if self._options['bias']:
            self._set_bias()
        self._options.pop('bias')
                
        for k, v in self._options.items():
            sys.stderr.write('Setting: {:50s} -> {:50s}\n'.format(k, str(v)))
            if k not in self.index.keys():
                if k == 'mode':
                    pass
                elif k == 'isUnix':
                    if v == 'yes':
                        for inst in self.input_xml.findall('./ffsocket'):
                            inst.set('mode', 'unix')
                    else:
                        for inst in self.input_xml.findall('./ffsocket'):
                            inst.set('mode', 'inet')
                elif k == 'title' or k == 'bias':
                    continue
                else:
                    raise(IndexError(
                        'Keyword: {} not found in the index'.format(k)))
            else:
                self._set_value(k, str(v))
            self.indent(self.input_xml)
            # etree.dump(self.input_xml)
        return etree.tostring(self.input_xml, method='xml', encoding='us-ascii')


class remTempEstimator(list):

    def __init__(self, tmin, tmax, N, steep):
        factor = 2  # To initialize the least square method
        f = optim.leastsq(self._tominimize, factor, args=(tmin, tmax, N, steep))[0][0]
        self.t_list = self._getTemps(tmin, N, f, steep)
        with open('TLIST.dat', 'w') as f:
            for t in self.t_list:
                f.write('{:12.6f}\n'.format(t))
#        print(self)

    def _tominimize(self, f, tmin, tmax, N, steep):
        temp_list = self._getTemps(tmin, N, f, steep)
        return tmax - temp_list[-1]

    def _getTemps(self, tmin, N, f, steep):

        rem_t = [tmin]
        while True:
            if len(rem_t) == N: break
            rem_t.append(rem_t[-1] + self._DeltaT(rem_t[-1], f, len(rem_t), steep))

        return rem_t


    def _DeltaT(self, T, f, n=1, c=1):
        return f * (np.exp(c*n) - np.exp(c*n-c))
        # return T * f



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
