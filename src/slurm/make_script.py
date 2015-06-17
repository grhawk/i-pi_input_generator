#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# Project:  inputsGen
# FileName: make_script
# Creation: Jun 17, 2015
#

"""Example Google style docstrings.

This module demonstrates documentation as specified by the `Google Python
Style Guide`_. Docstrings may extend over multiple lines. Sections are created
with a section header and a colon followed by a block of indented text.

Example:
  Examples can be given using either the ``Example`` or ``Examples``
  sections. Sections support any reStructuredText formatting, including
  literal blocks::

      $ python example_google.py

Section breaks are created by simply resuming unindented text. Section breaks
are also implicitly created anytime a new section starts.

Attributes:
  module_level_variable (int): Module level variables may be documented in
    either the ``Attributes`` section of the module docstring, or in an
    inline docstring immediately following the variable.

    Either form is acceptable, but the two should not be mixed. Choose
    one convention to document module level variables and be consistent
    with it.

.. _Google Python Style Guide:
   http://google-styleguide.googlecode.com/svn/trunk/pyguide.html

"""

import os
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


class sbatchDftbScript(object):
    def __init__(self, title='dftbJob', mem=1000, task_per_node=1):
        self.workdir = os.getcwd()
        self.title = title
        self.mem = mem
        self.nodes = 1
        self.ntasks_per_nodes = task_per_node
        self.stderr = os.path.join('/home/petragli/err/', str(title) + 'stderr_%j')
        self.stdout = os.path.join('/home/petragli/err/', str(title) + 'stdout_%j')
        self.inputfile = 'dftb_in.hsd'

        self.config = dict(
            sources=['/software/ENV/set_intel-134.sh', '/software/ENV/set_impi_413.sh'],
            bin='/home/petragli/Software/dftbp-ipi/prg_dftb/_obj_x86_64-linux-ifort-aries/dftb+',
            # bin='/home/petragli/MyCodes/dftbp-ipi/prg_dftb/_obj_x86_64-linux-gfortran/dftb+'
            )
        self.check_all()

    def check_all(self):
        if not os.path.isfile(self.inputfile):
            raise FileNotFound('INPUTFILE', self.inputfile)
#         if not os.path.isfile(self.config['bin']):
#             raise FileNotFound('BINFILE', self.config['bin'])

    def write(self):

        init = \
"""#!/bin/bash
#SBATCH -J {title}
#SBATCH -e {stderr}
#SBATCH -o {stdout}
#SBATCH --mem={mem}
#SBATCH --nodes={nodes}
#SBATCH --ntasks-per-node={ntasks_per_node}

INPUTFILE={inputfile}
WORKING_DIR={workdir}
TMP_DIR=$SLURM_TMPDIR

export OMP_NUM_THREADS={ntasks_per_node}
""".format
        sources = ''
        for s in self.config['sources']:
            sources += 'source {:s}\n'.format(s)

        functions = \
"""
function coping_back() {
    rsync -ch $TMP_DIR $WORKING_DIR
    if [[ -e $WORKING_DIR/RUNNING.lock ]]; then
        rm -f $WORKING_DIR/RUNNING.lock
    fi
}
trap 'coping_back' TERM EXIT
"""

        works = \
"""
cd $TMP_DIR
cp -ar $WORKING_DIR/dftb_in.hsd $TMP_DIR

touch $WORKING_DIR/RUNNING.lock
{bin} dftb_in.hsd >> dftb.out

exit($?)
""".format

        msg = \
            init(title=self.title,
                 stderr=self.stderr,
                 stdout=self.stdout,
                 mem=self.mem,
                 nodes=self.nodes,
                 ntasks_per_node=self.ntasks_per_nodes,
                 inputfile=self.inputfile,
                 workdir=self.workdir,
                 ) + \
            sources + \
            functions + \
            works(bin=self.config['bin'])

        return msg


class FileNotFound(Exception):
    def __init__(self, context, filename):
        sys.stderr.write('{} {} not found!\n'.format(context, filename))
        sys.exit(1)

if __name__ == '__main__':
    script = sbatchDftbScript()
    print(script.write())
