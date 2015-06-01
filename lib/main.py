#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 
# Project:    inputsGen
# FileName:   main
# Creation:   Jun 1, 2015
# Author:     Riccardo Petraglia
# Credits:    Riccardo Petraglia
# License:    GPLv2
# Maintainer: Riccardo Petraglia
# Email:      riccardo.petraglia@gmail.com
# Status:     development
#

""" Short docstring.

Long multiline description.

"""
#
# Often used modules:
# import subprocess
# import sys
# import os

# Other builtin modules you may like:
# import numpy as np

# Put here your own modules..
# sys.path.append('.')
# import ..

# Try determining the version from git:
# (uncomment with import subprocess if useful)
# try:
#     git_v = subprocess.check_output(['git', 'describe'])
# except:
#     git_v = 'Not Yet Tagged!'


import inputsCreator as ic

inp = ic.DftbInput('../example/tests/testfile.hsd')
inp.parameters['Hamiltonian_SCC'] = 'Yes'
inp.writeInput()
print (ic.__version__)

