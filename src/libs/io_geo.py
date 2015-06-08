#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# Project:  inputsGen
# FileName: xyz_geo
# Creation: Jun 2, 2015
#

"""Contains all the things to write and xyz files"""

import sys
from libs.geometry import Geometry
from libs.filetype import BannerLines
import numpy as np


# Try determining the version from git:
try:
    import subprocess
    git_v = subprocess.check_output(['git', 'describe'])
except subprocess.CalledProcessError:
    git_v = 'Not Yet Tagged!'


__author__ = 'Riccardo Petraglia'
__credits__ = ['Riccardo Petraglia']
__updated__ = "2015-06-08"
__license__ = 'GPLv2'
__version__ = git_v
__maintainer__ = 'Riccardo Petraglia'
__email__ = 'riccardo.petraglia@gmail.com'
__status__ = 'development'


class GeoIo(Geometry):

    def __init__(self):
        super().__init__()
        self.filepath = None

    def xyz_read(self, filepath):
        frame = 0
        atype = []
        coords = []
        with open(filepath) as f:
            for k, line in enumerate(f):
                if BannerLines().xyz.match(line):
                    natom = int(line)
                    frame += 1
                    if frame > 1: raise IsTrajectory(filepath)
                if k == 1: comment = line
                if k > 1:
                    tmp, x, y, z = line.split()
                    atype.append(tmp)
                    coords.append([float(x), float(y), float(z)])
        self.coords = np.array(coords)
        self.specienames = list(set(atype))
        self.nspecie = len(self.specienames)
        self.natom = natom
        self.comment = comment.strip()
        if len(self.coords) != self.natom:
            raise WrongNumberOfAtoms(self.natom, len(self.coords))
        for at in atype:
            self.indexes.append(self.specienames.index(at))
        if BannerLines().vector.match(self.comment):
            self.lattice = [float(i) for i in self.comment.split()]
            self.periodic = True

    def xyz_write(self):
        if not self.comment:
            self.comment = 'Written by inputsGen'
        if self.latvecs:
            self.comment = '{0:12.6f} {1:12.6f} {2:12.6}\n'.format(
                self.latvecs[0], self.latvecs[1], self.latvecs[2])
        xyz_format = '{name:3s}  {x:12.6f} {y:12.6f} {z:12.6f}\n'.format
        msg = '{:d}\n'.format(self.natom)
        msg += '{0:s}\n'.format(str(self.comment))
        for i, coord in enumerate(self.coords):
            msg += xyz_format(name=self.specienames[self.indexes[i]],
                              x=coord[0],
                              y=coord[1],
                              z=coord[2])
        return msg

    def gen_read(self, filepath):
        frame = 0
        coords = []
        with open(filepath) as f:
            for k, line in enumerate(f):
                if BannerLines().gen.match(line):
                    natom = int(line.split()[0])
                    mode = line.split()[1].strip()
                    supercell = mode == 'S'
                    cluster = mode == 'C'
                    crystal = mode == 'F'
                    if crystal:
                        raise NotImplementedError(
                            'F is not usable with this script')
                    if cluster or supercell: pass
                    frame += 1
                    if frame > 1: raise IsTrajectory(filepath)
                if k == 1: self.specienames = line.split()
                if k > 1 and k < 2 + natom:
                    _, tmp, x, y, z = line.split()
                    self.indexes.append(int(tmp) - 1)
                    coords.append([float(x), float(y), float(z)])
                if supercell and k > 1 + natom:
                    self.origin = [float(x) for x in line.split()]
                if supercell and k > 2 + natom:
                    self.lattice.append([float(x) for x in line.split()])
        self.coords = np.array(coords)
        self.natom = natom
        if len(self.coords) != self.natom:
            raise WrongNumberOfAtoms(self.natom, len(self.coords))

    def gen_write(self):
        gen_format = '{a:5d}  {b:3d}  {x:12.6f}  {y:12.6f}  {z:12.6f}\n'.format
        if self.periodic:
            mode = 'S'
            toappend = '{0:12.6f}  {0:12.6f}  {0:12.6f}\n'.format(self.origin)
            for vect in self.latvecs:
                toappend += '{0:12.6f}  {0:12.6f}  {0:12.6f}\n'.format(vect)
        else:
            mode = 'C'
            toappend = ''
        msg = '{0:5d}  {1:1s}\n'.format(self.natom, mode)
        msg += ' '.join(self.specienames)
        for i, coord in enumerate(self.coords):
            print(coord[0])
            msg += gen_format(a=i, b=self.indexes[i],
                              x=coord[0], y=coord[0], z=coord[0])
        msg += toappend
        return msg


class IsTrajectory(Exception):
    def __init__(self, filepath):
        msg = 'The file {} contains a trajectory.\n'.format(filepath)
        msg += 'Only single molecule format is supported\n'
        sys.stderr.write(msg)
        sys.exit(1)


class WrongNumberOfAtoms(Exception):
    def __init__(self, expected, found):
        msg = 'Readed {0:d} atoms while {1:d} were expected!\n'.format(
            found, expected)
        print(msg)
        sys.exit(1)
