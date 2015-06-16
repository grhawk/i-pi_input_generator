#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# Project:  inputsGen
# FileName: dftb_data
# Creation: Jun 9, 2015
#

"""Contains the data to run properly the dftb computation

"""

import sys

# Try determining the version from git:
try:
    import subprocess
    git_v = subprocess.check_output(['git', 'describe'])
except subprocess.CalledProcessError:
    git_v = 'Not Yet Tagged!'


__author__ = 'Riccardo Petraglia'
__credits__ = ['Riccardo Petraglia']
__updated__ = "2015-06-16"
__license__ = 'GPLv2'
__version__ = git_v
__maintainer__ = 'Riccardo Petraglia'
__email__ = 'riccardo.petraglia@gmail.com'
__status__ = 'development'


class DftbData(object):
    """Parameters set's data to write into the dftbp input.

    Some of the data needed to run a dftb computation with dftb+ must be
    written directly in the dftb+ input file. This class helps in storing and
    retrieving those data.

    Args:
        parameters_set: The name of the parameter set that is used.

    Note:
        The data are available for the 3ob set.
        Remember to upgrade this note each time you add a new set.
    """
    def __init__(self, parameters_set):
        self.parameters = parameters_set

        threeob_1_1 = dict(
            names=['3ob', '3ob_1_1', 'threeOb', 'threeob', 'threeOB', ],
            hubbard_derivs=dict(
                H=-0.1857,
                C=-0.1492,
                N=-0.1535,
                S=-0.11,
                O=-0.1575,
            ),
            damp_xh_exponent=4.0,
            max_angular_momentum=dict(
                H="s",
                C="p",
                N="p",
                S="d",
                O="p",
            )
        )

        print(parameters_set)
        if parameters_set in threeob_1_1['names']:
            self.prms = threeob_1_1
        else:
            raise ParametersSetNotFoundError(parameters_set)

    def find_data_per_atom(self, atype, data_type):
        """A method to retrieve the data for each property and for each atom.

        The fundamental method to retrieve data from the database contained in
        this class.

        Args:
            atype: the atom type as written in a regular xyz file
            data_type: can be hubbard_derivs or max_angular_momentum

        """
        self.find_data_per_method(data_type)
        if atype not in self.prms[data_type]:
            raise AtomTypeNotFoundError(atype)

        return self.prms[data_type][atype]

    def find_data_per_method(self, data_type):
        if data_type not in self.prms:
            raise DataTypeNotFoundError(data_type)
        return self.prms[data_type]



class ParametersSetNotFoundError(Exception):
    def __init__(self, parameters_set):
        msg = 'You asked for {} parameters set!!\n'.format(parameters_set)
        msg += 'The parameters set you specified is not available in the\n'
        msg += 'dftb_data module. Check the documentation of the module to\n'
        msg += 'see which parameters is available. If you need something\n'
        msg += 'different add them or ask riccardo how to add them.. ;)\n'
        sys.stderr.write(msg)
        sys.exit()


class DataTypeNotFoundError(Exception):
    def __init__(self, data_type):
        msg = 'You asked for {} data\n'.format(data_type)
        msg += 'This kind of data does not exists into the dftb framework\n'
        msg += 'Refer to the DFTB+ manual to understand what you are doing!\n'
        sys.stderr.write(msg)
        sys.exit()


class AtomTypeNotFoundError(Exception):
    def __init__(self, atype):
        msg = 'You asked for {0} atom from the {1} parameters set!!\n'.format(
            atype, self.parameters_set)
        msg += 'The atom you specified is not available into the selected\n'
        msg += 'parameters set. Check the documentation of the parameters set\n'
        msg += 'to see which atoms are available. If you need something\n'
        msg += 'different add them or ask riccardo how to add them.. ;)\n'
        sys.stderr.write(msg)
        sys.exit()
