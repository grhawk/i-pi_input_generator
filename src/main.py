#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# Project:  inputsGen
# FileName: main
# Creation: Jun 12, 2015
#

"""
Main file

"""

import sys
import os
heredir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(heredir, 'ports/port-for/'))

import argparse
import ports.ports_master as portsMaster
import ipi.input_ipi as ipi
import dftbp.input_dftb as dftb
from libs.io_geo import GeoIo


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


config = dict(
    SKfileLocation='/data2/Store/SK-parameters/3ob-1-1/',
    username='petragli'
)


def main():
    args = _validate_args(_parser())

    # Write data to the ipi input
    ipiI = ipi.InputIpi()
    for k, v in args.items():
        if k == 'mode': continue
        ipiI.set(k, v)

    with open('ipi_input.xml', 'wb') as ipif:
        # print(type(ipiI.create_input()))
        ipif.write(ipiI.create_input())

    print('Written IPI')

    # Write data to the dftb input
    geo = GeoIo()
    geo.xyz_read(args['xyzfile'])
    if not geo.periodic:
        geo.set_cell([50., 50., 50.])
    print(geo.natom)
    print('LATVECT:', geo.latvecs)
    dftbpI = dftb.InputDftb(geo, config['SKfileLocation'])
    dftbpI.add_keyword('Driver_Host', args['address'])
    dftbpI.add_keyword('Driver_Port', args['port'])
    dftbpI.add_keyword('Driver_isUnix', args['isUnix'])
    dftbpI.add_keyword('Hamiltonian_ThirdOrderFull', 'Yes')

    with open('dftb_in.hsd', 'w') as dftbf:
        dftbf.write(dftbpI.write())


def _validate_args(args):
    notNone_option = {}
    for k, v in args.items():
        if v is not None:
            print(k, v)
            notNone_option[k] = v
            if (isinstance(v, int) or isinstance(v, float)) and not (v == False or v == True):
                if not _ispositive(v):
                    raise(ValueError('The value of ' + str(k) + ' must be positive!'))

    if 'port' in notNone_option:
        port = notNone_option['port']
        if not portsMaster.is_port_free(port):
            raise(ValueError('The port choosen ({}) is not available. Do not specify any port!'.format(port)))
    else:
        notNone_option['port'] = portsMaster.giveme_a_port()

    if 'title' not in notNone_option:
        notNone_option['title'] = notNone_option['xyzfile']

    if notNone_option['isUnix']:
        notNone_option['isUnix'] = 'Yes'
        notNone_option['address'] = str(notNone_option['title']) + '_' + str(config['username'])
    else:
        notNone_option['isUnix'] = 'No'


    if notNone_option['mode'].lower() == 'rem':
        c1 = 'Tmin' not in notNone_option
        c2 = 'Tmax' not in notNone_option
        c3 = 'nrep' not in notNone_option
        c4 = 'rstride' not in notNone_option

        if c1 or c2 or c3 or c4:
                raise(RuntimeError('When you want to do rem, you have to specify everyting!'))

        notNone_option.pop('mode')
        notNone_option['rem'] = 'yes'

    return notNone_option


def _ispositive(number):
    return number > 0


def _parser():
    parser = argparse.ArgumentParser(
        description='Helps in build REM@DFTB input files.')

    rem = parser.add_argument_group('REM', 'REM variables')
    rem.add_argument('--Tmin',
                           action='store',
                           type=float,
                           help='Smallest REM temperature')

    rem.add_argument('--Tmax',
                           action='store',
                           type=float,
                           help='Highest REM temperature')

    rem.add_argument('--nrep',
                           action='store',
                           type=int,
                           help='Number of replicas')

    rem.add_argument('-rt', '--rstride',
                     action='store',
                     type=int,
                     help='Steps between two replica exchanging attemps')

    ensemble = parser.add_argument_group('Ensemble',
                                         'Parameters for the ensamble')
    ensemble.add_argument('--temperature',
                          action='store',
                          default=300.0,
                          type=float,
                          help='Temperature if not REM simulation')
    ensemble.add_argument('--timestep',
                          action='store',
                          default=0.5,
                          type=float,
                          help='Time step')

    initialize = parser.add_argument_group('Initialization',
                                           'Parameters to initialize the system')
    initialize.add_argument('xyzfile',
                            action='store',
                            type=str,
                            help='Geometry structure in xyz file')
    initialize.add_argument('--initial_temperature',
                            action='store',
                            default=300.0,
                            type=float,
                            help='Initial temperature for the simulation')

    ffsocket = parser.add_argument_group('FFSOCKET',
                                         'Sockets parameters')
    ffsocket.add_argument('--address',
                          action='store',
                          default='192.168.0.101',
                          type=str,
                          help='Ip address of the server')
    ffsocket.add_argument('--port',
                          action='store',
                          default=None,
                          type=int,
                          help='Port used by the socket. Leave it and I will try to find one')
    ffsocket.add_argument('--slots',
                          action='store',
                          default=2,
                          type=str,
                          help='Number of DFTB instance expected')
    ffsocket.add_argument('--timeout',
                          action='store',
                          default=60,
                          type=int,
                          help='Seconds to wait until consider a dftb instance DEAD!')
    ffsocket.add_argument('--isUnix', '--isunix',
                          action='store_true',
                          default=False,
                          dest='isUnix',
                          help='Select this option if you want to open a Unix Socket!.')

    general = parser.add_argument_group('General Parameters',
                                        'Parameters for the simulation')
    general.add_argument('--nstep',
                         action='store',
                         default=50000)
    general.add_argument('--mode',
                         action='store',
                         default='md',
                         choices=['md', 'rem'],
                         help='You can run REM or normal MD')

    general.add_argument('--title',
                         action='store',
                         default=None,
                         help='Set a title for the jobs otherwise it will be the name of the geometry file')

    return vars(parser.parse_args())

if __name__ == '__main__':
    main()
