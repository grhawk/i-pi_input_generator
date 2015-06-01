#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# Project:  inputsGen
# FileName: inputsCreator
# Creation: Jun 1, 2015
#

""" Title of Docstring.

Actual docsting here.

"""

# Often used modules:
import subprocess
# import sys
# import os

# Other builtin modules you may like:
# import numpy as np

# Put here your own modules..
# import ...

# Try determining the version from git:
try:
    git_v = subprocess.check_output(['git', 'describe'])
except:
    git_v = 'Not Yet Tagged!'


__author__ = 'Riccardo Petraglia'
__credits__ = ['Riccardo Petraglia']

__license__ = 'GPLv2'
__version__ = git_v
__maintainer__ = 'Riccardo Petraglia'
__email__ = 'riccardo.petraglia@gmail.com'
__status__ = 'development'


class GeneralInput(object):
    """Definition of a general input class
    
    This class is a parent of all the classes that will generate inputs.
    Right now it define the file path for the input in the his __init__.
    """
    
    def __init__(self, filepath):
        """Parents of the init input classes
        
        @param filepath: Define the filepath for the input file
        """
        
        self.filepath = filepath
        self.input_str = ''
        self.inputReady = False
    
    
    def writeInput(self):
        """Write the generated input to the filepath file
        
        """
        
        if self.inputReady:
            with open(self.filepath, 'w') as f:
                f.write(self.input_str)
        else:
            raise InputNotDefined
        

class DftbInput(GeneralInput):
    """
    """
    
    def __init__(self, filepath):
        super().__init__(filepath)
        
        self.parameters = dict(
            Hamiltonian_='DFTB',
            Driver_='ConjugateGradient',
            Driver_MaxForceComponent='1E-4',
            Driver_ConvergentForcesOnly = 'No',
            Driver_MaxSteps=0,
            Hamiltonian_SlaterKosterFiles_='Type2FileNames',
            Hamiltonian_SlaterKosterFiles_Prefix='slako_dir',
            Hamiltonian_SlaterKosterFiles_Separator='"-"',
            Hamiltonian_SlaterKosterFiles_Suffix='".skf"',
            Hamiltonian_SCC = 'No',
            Hamiltonian_Eigensolver = 'RelativelyRobust{}'
            )

        
        
    def dftbInput(self):

        #--------MAIN KEYWORDS-------
        previous_key = 'dummy_'
        myspace = ' '
        for key, value in sorted(self.parameters.items()):
            current_depth = key.rstrip('_').count('_')
            previous_depth = previous_key.rstrip('_').count('_')
            for my_backsclash in reversed(\
                range(previous_depth - current_depth)):
                self.input_str += (3 * (1 + my_backsclash) * myspace + '} \n')
            self.input_str += (3 * current_depth * myspace)
            if key.endswith('_'):
                self.input_str += (key.rstrip('_').rsplit('_')[-1] + \
                                  ' = ' + str(value) + '{ \n')
            elif key.count('_empty') == 1:
                self.input_str += (str(value) + ' \n')
            else:
                self.input_str += (key.rsplit('_')[-1] + ' = ' + str(value) + ' \n')
            previous_key = key
        current_depth = key.rstrip('_').count('_')
        for my_backsclash in reversed(range(current_depth)):
            self.input_str += (3 * my_backsclash * myspace + '} \n')
        #output to 'results.tag' file (which has proper formatting)
        self.input_str += ('Options { \n')
        self.input_str += ('   WriteResultsTag = Yes  \n')
        self.input_str += ('} \n')
        
        print('TEST')
        self.inputReady = True
        return
    
    def writeInput(self):
        self.dftbInput()
        super().writeInput(self)


class InputNotDefined(Exception):
    print('Input is not yet defined')