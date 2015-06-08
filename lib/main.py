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


# To test the dftbp module
# print('TEST')
# from dftbp import input_dftb
# test = dftbp.input_dftb.InputDftb()
# test.add_keyword('Port', 192, 'Driver', 'IPI')
# print(dftbp.input_dftb.__version__)
# print('ciao')

# To test the libs Module
from libs.io_geo import GeoIo

geo = GeoIo
geo.xyz_read('../example/test.xyz')

# geo = Xyz()

# print(geo.__version__)


