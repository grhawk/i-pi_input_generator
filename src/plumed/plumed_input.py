#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# Project:  inputsGen
# FileName: input_ipi
# Creation: Jun 9, 2015
#

"""This module take care of the plumed2 input and to generate a script with the rigth command.

This module provide a simple way to write the input for plumed2 and to generate
a script with the right command to call plumed2.

"""
import sys

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

class plumed2(object):
    pass


class connection(object):
    def __init__(self, at1, at2):
        self.bond = [int(at1), int(at2)]
        self.rbond = [int(at2), int(at1)]

    def __eq__(self, other):
#        print(other.bond)
        if other.bond == self.bond or other.bond == self.rbond:
            return True
        else:
            return False

    def __str__(self):
        msg = 'BOND1: {:4d} -- {:4d}\n'.format(self.bond[0], self.bond[1])
        return msg

class connectivity(object):
    def __init__(self):
        self.connectivity = []

    def add(self, at1, at2):
        new = connection(at1, at2)
        for con in self.connectivity:
            if new == con: return
        self.connectivity.append(new)

    def write(self):
        msg = ''
        for bond in self.connectivity:
            msg += str(bond)
        print(msg)

    def __iter__(self):
        return self.connectivity.__iter__()

