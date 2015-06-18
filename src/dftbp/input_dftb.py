#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Project:  inputsGen
# FileName: paramDFTB
# Creation: Jun 1, 2015
#

"""This module take care of the dftb input.

This module provide a default set of keywords and values for the dftb file.
Moreover the main class contains a method to write the parameters down in the
hsd format. The output of that method can be used directly as input for the
dftb+ code.
"""

import os
from dftbp.dftb_data import DftbData
from dftbp.dftb_data import DftbPreset
# from libs.geometry import Geometry as Structure

# Try determining the version from git:
try:
    import subprocess
    git_v = subprocess.check_output(['git', 'describe'])
except subprocess.CalledProcessError:
    git_v = 'Not Yet Tagged!'

__author__ = 'Riccardo Petraglia'
__credits__ = ['Riccardo Petraglia']
__updated__ = "2015-06-18"
__license__ = 'GPLv2'
__version__ = git_v
__maintainer__ = 'Riccardo Petraglia'
__email__ = 'riccardo.petraglia@gmail.com'
__status__ = 'development'


class InputDftb(dict):
    """A container for all the dftb paramters.

    This class provide a container for the dftb parameters. All the *optional*
    keyword you want to use in the input should be added thought the
    add_keyword method of this class.
    Keywords are memorized in a dictionary with their values. The key of the
    dictionary contains the keyword in a *string format*: the childrend are
    separated from the parents by underscores (_). That means that the port
    number lying in the driver class (when the driver is Ipi) is rapresented by
    the following code::

        Driver_port

    Adding an underscore at the end of a key will open a curly bracket in the
    hsd format.

    Args:
        Geometry: is a geometry class defined in the libs module
        parameters_folder: absolute path to the folder containing the parameters
        parameters_set: name of the parameters set to be used. If None the
                    parameters set is extracted as the last directory in the
                    parameters_folder

    Note:
        The default keywords have to be defined in the *string* format as
        described in the class docstring and are contained in the
        default_prms dictionary.

    """

    def __init__(self, Geometry, parameters_folder):
        super().__init__()

        default_prms = dict(
            Geometry_='GenFormat',
            Geometry_empty=Geometry.gen_write(),
            Driver_='Ipi',
            Hamiltonian_='DFTB',
            Hamiltonian_SlaterKosterFiles_='Type2FileNames',
            Hamiltonian_SlaterKosterFiles_Separator='"-"',
            Hamiltonian_SlaterKosterFiles_Suffix='".skf"',
            Options_='',
            Options_WriteResultsTag='No',
            Options_WriteDetailedOut='No',
            Options_WriteBandOut='No',
        )

        for k, v in default_prms.items():
            self.add_keyword(k, v)

        self.Geometry = Geometry
        self.parameters_folder = parameters_folder
        self.parameters_set = None

    def _set_atoms_property(self):
        """Private method to retrieve the data per atom/parameters_set.

        This method provide the data bind to the parameters set.

        Args:
            Geometry: geometry object as defined in the respective class under
                    the libs module.
            parameters_set: name of the parameters you need the data

        """
        Geometry = self.Geometry
        parameters_set = self.parameters_set
        data = DftbData(parameters_set)

        for atype in Geometry.specienames:
            self.add_keyword('Hamiltonian_MaxAngularMomentum_{}'.format(atype),
                             data.find_data_per_atom(atype,
                                                     'max_angular_momentum'))

        isThirdOrder = 'Hamiltonian_ThirdOrder' in self and \
            self['Hamiltonian_ThirdOrder'] == 'Yes'
        isThirdOrderFull = 'Hamiltonian_ThirdOrderFull' in self and \
            self['Hamiltonian_ThirdOrderFull'] == 'Yes'
        if isThirdOrder or isThirdOrderFull:
            for atype in Geometry.specienames:
                self.add_keyword('Hamiltonian_HubbardDerivs_{}'.format(atype),
                                 data.find_data_per_atom(atype,
                                                         'hubbard_derivs'))
                self.add_keyword('Hamiltonian_DampXHExponent', data.find_data_per_method('damp_xh_exponent'))

    def write(self):
        """This method has been mostly copied from the ASE package.

        This method write all the keyword in the expected hsd format. This
        method is responsible for the conversion of the underscores in curly
        brackets.

        """
        self._set_atoms_property()

        input_str = ''
        previous_key = 'dummy_'
        myspace = ' '
        for key, value in sorted(self.items()):
            current_depth = key.rstrip('_').count('_')
            previous_depth = previous_key.rstrip('_').count('_')
            for my_backsclash in reversed(
                    range(previous_depth - current_depth)):
                input_str += (3 * (1 + my_backsclash) * myspace + '} \n')
            input_str += (3 * current_depth * myspace)
            if key.endswith('_'):
                input_str += (key.rstrip('_').rsplit('_')[-1] +
                              ' = ' + str(value) + '{ \n')
            elif key.count('_empty') == 1:
                input_str += (str(value) + ' \n')
            else:
                input_str += (key.rsplit('_')[-1] + ' = ' + str(value) + ' \n')
            previous_key = key
        current_depth = key.rstrip('_').count('_')
        for my_backsclash in reversed(range(current_depth)):
            input_str += (3 * my_backsclash * myspace + '} \n')
        return input_str

    def _make_string_keyword(self, keyword, parents):
        """Convert a keyword with his parents in a *string formatted* keyword.

        Take the keyword and his parents as argument and generate a *string
        formatte* keyword.

        Args:
            keyword: the keyword you want to add
            parents: a list of words that are parents of the keyword in the hsd
            dftb+ format.

        """
        # FIXME: This could have some issue!!
        if parents:
            key = '_'.join(parents) + '_' + keyword
        else:
            key = keyword
        return key

    def add_keyword(self, keyword, value, *parents):
        """This method is used to add keyword to the container.

        This method allows to add keywords to the dictionary that contains all
        the couple keyword values to insert in the hsd file.

        Note:
            The keyword can be in the *string* format (see class docstring) or
            the parents can be specified in the *parents* list.

        Args:
            keyword: the keyword to be added to the dftb+ input
            value: the value the keyword should assume
            *parents: if the keyword is not in the *string* format you can
                specify the parents separeted by comma.

        """
        key = self._make_string_keyword(keyword, parents)

        # If parents are not existing, add them before to add the keyword
        keys = key.split('_')
        keyw = ''
        for k in keys[:-1]:
            keyw += '{}_'.format(k)
            if keyw not in self.keys():
                super().__setitem__(keyw, '')

        super().__setitem__(key, value)

    def del_keyword(self, keyword, *parents):
        """This method is used to delete keyword from the container.

        This method allow the deletion of keyword from the dictionary that
        contains all the couple keyword value to insert in the hsd file.

        Note:
            The keyword can be in the *string* format (see class docstring) or
            the parents can be specified in the *parents* list.

        Args:
            keyword: the keyword to be deleted from the dftb+ input
            *parents: if the keyword is not in the *string* format you can
                specify the parents separeted by comma.

        """
        key = self._make_string_keyword(keyword, parents)

        if key not in self.keys(): raise NotExistingKeyword(key)

        super().__delattr__(key)

    def change_keyword(self, keyword, value, *parents):
        """This method is used to change a keyword's value in the container.

        This method allows to change the value of a keyword already existing
        in the dictionary that contains all the couple keyword values to insert
        in the hsd file.

        Note:
            The keyword can be in the *string* format (see class docstring) or
            the parents can be specified in the *parents* list.

        Args:
            keyword: the keyword to be changed to the dftb+ input
            value: the new value the keyword should assume
            *parents: if the keyword is not in the *string* format you can
                specify the parents separeted by comma.

        """
        key = self._make_string_keyword(keyword, parents)

        if key in self.items(): raise NotExistingKeyword(key, value)

        super().__setitem__(keyword, value)

    def __setitem__(self, *args, **kwargs):
        """Just turning off the usual method to add data to a dictionary.

        Thinking to the future deleting this method could be useful

        """
        raise AlternativeMethod('__setitem__', 'change_keyword or add_keyword')

    def __delitem__(self, *args, **kwargs):
        """Just turning off the usual method to add data to a dictionary.

        Thinking to the future deleting this method could be useful

        """
        raise AlternativeMethod('__delitem__', 'del_keyword')

    def set_preset(self, preset):
        param = DftbPreset().get(preset)
        self.parameters_set = param.pop('_parameters_set')
        self.skdir = param.pop('_sk_directory')
        for k, v in param.items():
            self.add_keyword(k, v)

        self.add_keyword('Hamiltonian_SlaterKosterFiles_Prefix',
                         os.path.join(self.parameters_folder, self.skdir) + '/')


class AlreadyExistingKeyword(Exception):
    """Exception raised when trying to add an existing keyword.

    Handle the situation when the user is trying to add an existing keyword
    to the dictionary.

    Args:
        keyword: the keyword in *string format* that you want to add
        value: the keyword's value

    """
    def __init__(self, keyword, value):
        super().__init__()
        import sys
        msg = 'The keyword is already existing in the dictionary\n'
        msg += 'Use the method change keyword instead\n'
        msg += 'Keyword: {}\n'.format(keyword)
        msg += 'Value: {}\n'.format(value)
        sys.stderr.write(msg)
        sys.exit(1)


class NotExistingKeyword(Exception):
    """Exception raised when trying to modify an not existing keyword.

    Handle the situation when the user is trying to modify a keyword that does
    not exist.

    Args:
        keyword: the keyword in *string format* that you want to add
        value: the keyword's value

    """
    def __init__(self, keyword, value='Undefined'):
        super().__init__()
        import sys
        msg = 'The keyword {} does not exist!\n'.format(keyword)
        msg += 'Use the method add keyword instead\n'
        msg += 'Keyword: {}\n'.format(keyword)
        msg += 'Value: {}\n'.format(value)
        sys.stderr.write(msg)
        sys.exit(1)


class AlternativeMethod(Exception):
    """Exception raised when using the wrong method.

    In order to save time on possible modification of the class, some of the
    normal method for dictionary are hindered. This exception show which method
    one should use instead of the one used.

    Args:
        used: the method used by the user
        touse: the method the user should have used
    """
    def __init__(self, used, touse):
        super().__init__()
        import sys
        msg = 'You are not allowed to use the method {}\n'.format(used)
        msg += 'Try with {} instead!\n'.format(touse)
        sys.stderr.write(msg)
        sys.exit(1)
