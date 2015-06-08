#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# Project:  inputsGen
# FileName: geo_gen
# Creation: Jun 2, 2015
#

"""This module allow to transfor an xyz file in an gen file.

This module is mostly stolen from the dftb+ package. It contains a couple of
class and methods to transform an xyz file in a gen file: the files dftb+ can
read.

"""

import numpy as np
import numpy.linalg as la

# Try determining the version from git:
try:
    import subprocess
    git_v = subprocess.check_output(['git', 'describe'])
except subprocess.CalledProcessError:
    git_v = 'Not Yet Tagged!'


__author__ = 'Riccardo Petraglia'
__credits__ = ['Riccardo Petraglia']
__updated__ = "2015-06-02"
__license__ = 'GPLv2'
__version__ = git_v
__maintainer__ = 'Riccardo Petraglia'
__email__ = 'riccardo.petraglia@gmail.com'
__status__ = 'development'

class Geometry(object):
    """Atomic geometry representation.

    Contains all the variable to define a molecular geometry. The geometry can
    be read/written in xyz or gen format.

    Note:
        The relative coordinates are not implemented!

    Args:
        specienames: Name of atomtypes which can be found in the geometry.
        nspecie: Number of species.
        indexes: For each atom the index of the corresponding specie
            in specienames.
        natom: Number of atoms.
        coords: xyz coordinates of the atoms.
        origin: Origin.
        periodic: True if the structure is periodic.
        latvecs: Lattice vectors (None for non-periodic structures).

    """
    def __init__(self):
        self.specienames = []
        self.nspecie = None
        self.indexes = []
        self.natom = None
        self.coords = []
        self.origin = None
        self.periodic = None
        self.latvecs = []
        self.comment = None

    def read_xyz(self, filep):
        pass

    def read_gen(self):
        pass

    def write_xyz(self):
        pass

    def write_gen(self):
        pass

