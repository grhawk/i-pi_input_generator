#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# Project:  inputsGen
# FileName: xyz_geo
# Creation: Jun 2, 2015
#

"""Contains all the things to write and read structure files"""

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
__updated__ = "2015-06-18"
__license__ = 'GPLv2'
__version__ = git_v
__maintainer__ = 'Riccardo Petraglia'
__email__ = 'riccardo.petraglia@gmail.com'
__status__ = 'development'


class GeoIo(Geometry):
    """All the stuff to read and write geometry files.

    It inherits from the Geometry class.

    """
    def __init__(self):
        super().__init__()
        self.filepath = None

    def xyz_read(self, filepath):
        """Read the xyz geometry from a file given as argument.

        Read the geometry from a file given as argument. The parsing process is
        based on both regular expression and expected position. If the xyz file
        has a different format than the expected one, unpredictable effect could
        arise.

        Args:
            filepath: the path of the file to be readed.

        Todo:
            This should be implemented to work with file objects intead of path.

        """
        frame = 0
        atype = []
        coords = []
        with open(filepath) as f:
            for k, line in enumerate(f):
                # Check if first line is an integer.
                if BannerLines().xyz.match(line):
                    natom = int(line)
                    frame += 1
                    # If the file contains more than one line with one only
                    # integer then the file is considered a trajectory

                    if frame > 1: raise IsTrajectory(filepath)

                if k == 1: comment = line  # The second line is the comment
                if k > 1:
                    # All the following line will
                    # contains all the atom coords.
                    words = line.split()
                    if len(words) == 4:
                        tmp, x, y, z = line.split()
                        atype.append(tmp)
                        coords.append([float(x), float(y), float(z)])

        self.coords = np.array(coords)
        self.specienames = list(set(atype))
        self.nspecie = len(self.specienames)
        self.natom = natom
        self.comment = comment.strip()
        if len(self.coords) != self.natom:  # Just check if the number of coords
                                            # is compatible with the number of
                                            # declare atoms
            raise WrongNumberOfAtoms(self.natom, len(self.coords))
        for at in atype:  # Build the indexes
            self.indexes.append(self.specienames.index(at))

    def xyz_write(self):
        """Return the geometry stored in the instance in the xyz format.

        After a geometry has been red, this method will return the geometry
        in the xyz format.

        Todo:
            The comment should contains the lattice vectors if the structure is
            periodic.

        """
        if not self.comment:
            self.comment = 'Written by inputsGen'
        if self.latvecs:
            self.comment = 'This structure is in a periodic system!!'
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
        """Read the gen geometry from a file given as argument.

        Read the geometry from a file given as argument. The parsing process is
        based on both regular expression and expected position. If the gen file
        has a different format than the expected one, unpredictable effect could
        arise.

        Args:
            filepath: the path of the file to be readed.

        Todo:
            This should be implemented to work with file objects intead of path.
            Implement the fractional coordinates (low priority)
        """
        frame = 0
        coords = []
        with open(filepath) as f:
            for k, line in enumerate(f):
                if BannerLines().gen.match(line):  # Check if the first line is
                                                # the first line matches the
                                                # expected format
                    natom = int(line.split()[0])
                    mode = line.split()[1].strip()
                    supercell = mode == 'S'
                    cluster = mode == 'C'
                    crystal = mode == 'F'
                    if crystal:
                        # The fractional coordinates
                        # are not implemented!
                        raise NotImplementedError(
                            'F is not usable with this script')
                    # Just to avoid error style error and to be consistent
                    if cluster or supercell: pass
                    frame += 1
                    # If there are more lines with the "banner" format
                    # raise the error
                    if frame > 1: raise IsTrajectory(filepath)

                if k == 1: self.specienames = line.split()
                if k > 1 and k < 2 + natom:
                    _, tmp, x, y, z = line.split()
                    self.indexes.append(int(tmp) - 1)
                    coords.append([float(x), float(y), float(z)])
                if supercell and k > 2 + natom:
                    self.origin = [float(x) for x in line.split()]
                if supercell and k > 3 + natom:
                    self.lattice.append([float(x) for x in line.split()])
        self.coords = np.array(coords)
        self.natom = natom
        if len(self.coords) != self.natom:
            raise WrongNumberOfAtoms(self.natom, len(self.coords))

    def gen_write(self):
        """Return the geometry stored in the instance in the gen format.

        After a geometry has been red, this method will return the geometry
        in the gen format.

        Todo:

        """
        gen_format = '{a:5d}  {b:3d}  {x:12.6f}  {y:12.6f}  {z:12.6f}\n'.format
        if self.periodic:
            mode = 'S'
            print (self.origin)
            toappend = ' '.join(map(lambda x: str(x), self.origin)) + '\n'
            for vect in self.latvecs:
                toappend += ' '.join(map(lambda x: str(x), vect)) + '\n'
        else:
            mode = 'C'
            toappend = ''
        msg = '{0:5d}  {1:1s}\n'.format(self.natom, mode)
        msg += ' '.join(self.specienames) + '\n'
        for i, coord in enumerate(self.coords):
            print(coord)
            msg += gen_format(a=i, b=self.indexes[i] + 1,
                              x=coord[0], y=coord[1], z=coord[2])
        msg += toappend
        return msg


class IsTrajectory(Exception):
    """If the file is a trajectory while a single structure was expected.

    Right now most of the stuff are implemented for single structure files. If
    the used structure is in a trajectory format raise this error.

    Args:
        filepath: Name of the file containing the unexpected format.

    """
    def __init__(self, filepath):
        msg = 'The file {} contains a trajectory.\n'.format(filepath)
        msg += 'Only single molecule format is supported\n'
        sys.stderr.write(msg)
        sys.exit(1)


class WrongNumberOfAtoms(Exception):
    """ If the declared number and the number of coordinates do not match.

    This is mostly for debugging purpose. Anyway this is raised when the number
    of atoms declared in the beginning of the structure file does not match with
    the number of atoms effectively present in the file.

    Args:
        expected: number of atoms declared in the file format.
        found: number of coordinates effectively found in the file.

    """
    def __init__(self, expected, found):
        msg = 'Readed {0:d} atoms while {1:d} were expected!\n'.format(
            found, expected)
        print(msg)
        sys.exit(1)
