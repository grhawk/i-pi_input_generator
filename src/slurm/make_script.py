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
import shutil
import re

# Try determining the version from git:
try:
    import subprocess
    DEVNULL = open(os.devnull, 'w')
    GIT_V = subprocess.check_output(['git', 'describe'],
                                    stderr=DEVNULL)
except subprocess.CalledProcessError:
    GIT_V = 'Not Yet Tagged!'


__author__ = 'Riccardo Petraglia'
__credits__ = ['Riccardo Petraglia']
__updated__ = "2016-06-24"
__license__ = 'GPLv2'
__version__ = GIT_V
__maintainer__ = 'Riccardo Petraglia'
__email__ = 'riccardo.petraglia@gmail.com'
__status__ = 'development'


class SbatchDftbScript(object):
    """ Create the sbatch file for dftb+.
    """
    # pylint: disable=too-many-instance-attributes
    # Maybe pylint is right.... btw

    def __init__(self, title='dftbJob', mem=1000, task_per_node=1,
                 executable='dftb+', user='student'):
        self.workdir = '$PWD'
        self.title = os.path.basename(title)
        self.mem = mem
        self.nodes = 1
        self.ntasks_per_nodes = task_per_node
        self.stderr = os.path.join('/home/', user, '/err/',
                                   os.path.basename(str(title)) + 'stderr_%j')
        self.stdout = os.path.join('/home/', user, '/err/',
                                   os.path.basename(str(title)) + 'stdout_%j')
        self.inputfile = 'dftb_in.hsd'
        self.outputfile = 'dftb.out'

        self.config = dict(
            sources=['intel/15.0.3',],
            bin=executable,
        )

    def check_all(self):
        """ Validate all the parameters.
        """

        if not os.path.isfile(self.inputfile):
            raise FileNotFound('INPUTFILE', self.inputfile)

        # If needed copy the input file to the "right" name
        if self.inputfile != 'dftb_in.hsd':
            shutil.copy2(self.inputfile, 'dftb_in.hsd')
            self.outputfile = self.inputfile[:-3] + 'out'

        # I do not understand the meaining of the following!
        with open(self.inputfile) as ifile:
            for line in ifile:
                if line.find('IPI') >= 0 and re.match(r'^\s*\#.*$', line):
                    self.outputdir = '.'
                else:
                    self.outputdir = self.workdir

        # Check if the stdout and stderr are writable
        for path in [self.stderr, self.stdout]:
            if not os.access(path, os.W_OK):
                raise(PermissionError('The directory {:s} is not writable!'.format(str(path))))

    def write(self):
        """ Write the sbatch file.
        """
        self.check_all()

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
            sources += 'module load {:s}\n'.format(s)

        functions = \
            """
function coping_back() {
    rsync -ca $TMP_DIR/ $WORKING_DIR/
    if [[ -e $WORKING_DIR/RUNNING_DFTBP.lock ]]; then
        rm -f $WORKING_DIR/RUNNING_DFTBP.lock
    fi
}

trap 'coping_back' TERM EXIT

"""

        works = \
            """
cd $TMP_DIR
cp -ar $WORKING_DIR/dftb_in.hsd $TMP_DIR

touch $WORKING_DIR/RUNNING_DFTBP.lock
{bin} dftb_in.hsd > {outputdir}/{outputfile}

exit()
""".format

        msg = \
              init(title=self.title,
                   stderr=self.stderr,
                   stdout=self.stdout,
                   mem=self.mem,
                   nodes=self.nodes,
                   ntasks_per_node=self.ntasks_per_nodes,
                   inputfile=self.inputfile,
                   workdir=self.workdir, ) + \
              sources + \
              functions + \
              works(bin=self.config['bin'],
                    outputfile=self.outputfile,
                    outputdir=self.outputdir)

        return msg


class FileNotFound(Exception):
    def __init__(self, context, filename):
        sys.stderr.write('{} {} not found!\n'.format(context, filename))
        sys.exit(1)

if __name__ == '__main__':
    script = sbatchDftbScript()
    print(script.write())
