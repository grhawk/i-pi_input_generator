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
    def __init__(self, xyzpath=None, options=None):
        self.options = options
        pdbp = xyzpath[:-4]+'.pdb'
        
        self.connections = connectivity()
    
        with open(pdbp) as pdbf:
            for line in pdbf:
                if line.find('CONECT') > -1:
                    # print(line)
                    atoms = line.split()[1:]
                    for at in atoms[1:]:
                        self.connections.add(atoms[0], at)

    def write(self, outfile):
        distance_tmpl = 'DISTANCE ATOMS={at1:d},{at2:d} LABEL=b{at1:d}{at2:d}\n'
        restraint_tmpl = 'RESTRAINT ARG=b{at1:d}{at2:d} AT=0.14 KAPPA=2000.0 LABEL=r{at1:d}{at2:d}\n'
        msg = '# Plumed input generated automatically by inputsGen\n'
        for bond in self.connections:
            msg += distance_tmpl.format(at1=bond.bond[0], at2=bond.bond[1])

        msg += '\n\n\n'
        for bond in self.connections:
            msg += restraint_tmpl.format(at1=bond.bond[0], at2=bond.bond[1])

        with open(outfile, 'w') as outf:
            outf.write(msg+'\n')

        msg = '#!/bin/bash\n'
        msg += '#SBATCH -J plumed-pippopluto_title\n'
        msg += '#SBATCH -e /home/petragli/err/pippopluto_titlestderr_%j\n'
        msg += '#SBATCH -o /home/petragli/err/pippopluto_titlestdout_%j\n'
        msg += '#SBATCH --mem=1000\n'
        msg += '#SBATCH --nodes=1\n'
        msg += '#SBATCH --ntasks-per-node=1\n'
        msg += '\n'

        msg += '''

WORKING_DIR=$PWD
TMPDIR=$SLURM_TMPDIR

function coping_back() {
    rsync -ca $TMPDIR/ $WORKING_DIR/
    if [[ -e $WORKING_DIR/RUNNING_PLUMED.lock ]]; then
        rm -f $WORKING_DIR/RUNNING_PLUMED.lock
    fi
}

trap 'coping_back' TERM EXIT

cd $TMPDIR
cp -ar $WORKING_DIR/plumed.dat $TMPDIR
touch $WORKING_DIR/RUNNING_plumed.lock

source ~/REM@DFTB-bias/env/set_tree.sh
source ~/REM@DFTB-bias/env/set_plumed.sh

'''
        msg += 'plumed socket --plumed {outfile:s} --host {address:s} --port {port:s} > $WORKING_DIR/plumed.out\n'.format(outfile=outfile, address=self.options['address'], port=str(self.options['port_bias']))
        msg += '\nexit\n'

        
        with open('plumed.sbatch', 'w') as outf:
            outf.write(msg)
            

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

