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
heredir = os.path.dirname(os.path.abspath(os.path.realpath(sys.argv[0])))
sys.path.append(os.path.join(heredir, 'ports/port-for'))

import argparse
import stat
import ports.ports_master as portsMaster
import ipi.input_ipi as ipi
import dftbp.input_dftb as dftb
from libs.io_geo import GeoIo
from slurm.make_script import sbatchDftbScript as sbatch
from slurm.make_runMany import runManyDftbScript as rMany
from slurm.make_runMany import runManyPlumedScript as rPMany
from plumed.plumed_input import plumed2 as plmd2

# Try determining the version from git:
try:
    import subprocess
    git_v = subprocess.check_output(['git', 'describe'],
                                    stderr=subprocess.DEVNULL)
except subprocess.CalledProcessError:
    git_v = b'Not Yet Tagged!'


__author__ = 'Riccardo Petraglia'
__credits__ = ['Riccardo Petraglia']
__updated__ = "2015-06-18"
__license__ = 'GPLv2'
__version__ = git_v
__maintainer__ = 'Riccardo Petraglia'
__email__ = 'riccardo.petraglia@gmail.com'
__status__ = 'development'


config = dict(
    SKfileLocation='/home/petragli/remd@dftb3/slako/',
    username=os.getcwd().split('/')[2]
)


def main():
    args = _validate_args(_parser())

    if args['rem'] == 'yes':
        title_for_sbatch = 'pippopluto_title'
    else:
        title_for_sbatch = args['title']

    sbatch_script = sbatch(title=title_for_sbatch,
                           mem=args['mem'],
                           task_per_node=args['processors'],
                           executable=args['dftb_exe'],
                           user=config['username'])
    args.pop('mem')
    args.pop('processors')
    args.pop('dftb_exe')

    if args['bias']:
        if args['isUnix']:
            msg = 'Bias can be used only over internet, unix not implemented.'
            raise(NotImplementedError(msg))
        if not os.path.isfile(args['xyzfile'][:-4]+'.pdb'):
            print(args['xyzfile'][:-4]+'.pdb')
            msg = 'FileNotFound: {out:s}.\n\n'\
                  'The command:\nobabel {inf:s} -O{out:s}\ncan helps.'.format(
                      out=args['xyzfile'][:-4]+'.pdb', inf=args['xyzfile'])
            raise(IOError(msg))
        plmd2(args['xyzfile'], options=args).write('plumed.dat')
        rmscript = rPMany(nreps=args['slots'],
                         title=args['title']).write()
        with open('runManyPlumed.sh', 'w') as runManyf:
            runManyf.write(rmscript)
        st = os.stat('runManyPlumed.sh')
        os.chmod('runManyPlumed.sh', st.st_mode | stat.S_IEXEC)



    # Write data to the dftb input
    geo = GeoIo()
    geo.xyz_read(args['xyzfile'])
    if not geo.periodic:
        geo.set_cell([100., 100., 100.])
    dftbpI = dftb.InputDftb(geo, config['SKfileLocation'])
    dftbpI.add_keyword('Driver_Protocol', 'i-PI{}')
    dftbpI.add_keyword('Driver_MaxSteps', 10000000)
    if args['isUnix']:
        dftbpI.add_keyword('Driver_File', args['address'])
    else:
        dftbpI.add_keyword('Driver_Host', args['address'])
        dftbpI.add_keyword('Driver_Port', args['port'])
    if not args.pop('ddmc'):
        dftbpI.add_keyword('Hamiltonian_Dispersion_', 'LennardJones')
        dftbpI.add_keyword('Hamiltonian_Dispersion_Parameters','UFFParameters{}')
    else:
        dftbpI.add_keyword('Hamiltonian_Dispersion', 'dDMC {}')

    dftbpI.set_preset(args.pop('dftb_type'))

    with open('dftb_in.hsd', 'w') as dftbf:
        dftbf.write(dftbpI.write())

    # Write data to the ipi input
    ipiI = ipi.InputIpi()
    for k, v in args.items():
        if k == 'mode': continue
        ipiI.set(k, v)

    with open('ipi_input.xml', 'wb') as ipif:
        # print(type(ipiI.create_input()))
        ipif.write(ipiI.create_input())

    with open('dftbp.sbatch', 'w') as sbatchf:
        sbatchf.write(sbatch_script.write())

    # if args['rem'] == 'yes':
    rmscript = rMany(nreps=args['slots'],
                     title=args['title']).write()
    with open('runMany.sh', 'w') as runManyf:
        runManyf.write(rmscript)
    st = os.stat('runMany.sh')
    os.chmod('runMany.sh', st.st_mode | stat.S_IEXEC)


def _validate_args(args):
    notNone_option = {}
    for k, v in args.items():
        if v is not None:
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

    if notNone_option['bias']:
        notNone_option['port_bias'] = portsMaster.giveme_a_port()

    if 'title' not in notNone_option:
        notNone_option['title'] = notNone_option['xyzfile']

    if notNone_option['isUnix']:
        notNone_option['isUnix'] = True
        notNone_option['address'] = str(notNone_option['title']) + '_' + str(config['username'])
    else:
        notNone_option['isUnix'] = False


    notNone_option['rem'] = 'no'
    if notNone_option['mode'].lower() == 'rem':
        c1 = 'Tmin' not in notNone_option
        c2 = 'Tmax' not in notNone_option
        c3 = 'nrep' not in notNone_option
        c4 = 'rstride' not in notNone_option
        c5 = 'steep' not in notNone_option

        if c1 or c2 or c3 or c4 or c5:
                raise(RuntimeError('When you want to do rem, you have to specify everyting!'))

        notNone_option.pop('mode')
        notNone_option['rem'] = 'yes'
        notNone_option['slots'] = notNone_option['nrep']

    return notNone_option


def _ispositive(number):
    return number > 0


def _parser():
    parser = argparse.ArgumentParser(
        description='Helps in building REM@DFTB input files.')

    rem = parser.add_argument_group('REM', 'REM variables')
    rem.add_argument('--Tmin',
                           action='store',
                           type=float,
                           help='Smallest REM temperature')

    rem.add_argument('--Tmax',
                           action='store',
                           type=float,
                           help='Highest REM temperature')

    rem.add_argument('--steep',
                           action='store',
                           default=0.06,
                           type=float,
                           help='Steep of the temperature increases')

    rem.add_argument('--nrep',
                           action='store',
                           type=int,
                           help='Number of replicas')

    rem.add_argument('-rt', '--rstride',
                     action='store',
                     default=50,
                     type=int,
                     help='Steps between two replica exchanging attemps')

    rem.add_argument( '--bias',
                     action='store_true',
                     default=False,
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
                          default=0.25,
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
                          default='192.168.100.1',
                          type=str,
                          help='Ip address of the server')
    ffsocket.add_argument('--port',
                          action='store',
                          default=None,
                          type=int,
                          help='Port used by the socket. Leave it and I will try to find one')
    ffsocket.add_argument('--slots',
                          action='store',
                          default=1,
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
                         default=500000)
    general.add_argument('--mode',
                         action='store',
                         default='md',
                         choices=['md', 'rem'],
                         help='You can run REM or normal MD')

    dftbp = parser.add_argument_group('DFTB parameters',
                                      'Options to set the DFTB run')
    dftbp.add_argument('--dftb-type',
                       action='store',
                       default='3ob31',
                       choices=['3ob', 'OCo','3ob31'],
                       help='Set the dftbp parameters as you plese')
    dftbp.add_argument('--dftb-exe',
                       action='store',
                       default='dftb+',
                       help='Set the dftb executable path')
    dftbp.add_argument('--ddmc',
                       action='store_true',
                       default=False,
                       help='If specified will use ddmc instead of UFF dispersion correction')

    submit = parser.add_argument_group('Submitting parameters',
                                       'Setting to create the sbatch script')
    submit.add_argument('--title',
                         action='store',
                         default=None,
                         help='Set a title for the jobs otherwise it will be the name of the geometry file')
    submit.add_argument('--processors', '-p',
                        action='store',
                        default=1,
                        help='Number of process for each DFTB+ instance')
    submit.add_argument('--mem', '-m',
                        action='store',
                        default=1000,
                        help='Memeory requested for each DFTB+ instance')
    parser.add_argument('--version', '-v',
                        action='version',
                        version='%(prog)s ' + str(git_v, encoding='UTF-8'))


    return vars(parser.parse_args())

if __name__ == '__main__':
    main()
