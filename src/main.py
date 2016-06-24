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
HEREDIR = os.path.dirname(os.path.abspath(os.path.realpath(sys.argv[0])))
sys.path.append(os.path.join(HEREDIR, 'ports/port-for'))

import argparse
import stat
import ports.ports_master as portsMaster
import ipi.input_ipi as ipi
import dftbp.input_dftb as dftb
from libs.io_geo import GeoIo
from slurm.make_script import SbatchDftbScript as sbatch
from slurm.make_runMany import runManyDftbScript as rMany
from slurm.make_runMany import runManyPlumedScript as rPMany
from plumed.plumed_input import plumed2 as plmd2

# Try determining the version from git:
try:
    import subprocess
    DEVNULL = open(os.devnull, 'w')
    GIT_V = subprocess.check_output(['git', 'describe'],
                                    stderr=DEVNULL)
except subprocess.CalledProcessError:
    GIT_V = b'Not Yet Tagged!'


__author__ = 'Riccardo Petraglia'
__credits__ = ['Riccardo Petraglia']
__updated__ = "2015-06-18"
__license__ = 'GPLv2'
__version__ = GIT_V
__maintainer__ = 'Riccardo Petraglia'
__email__ = 'riccardo.petraglia@gmail.com'
__status__ = 'development'


config = dict(
    SKfileLocation='/home/petragli/remd@dftb3/slako/',
    username=os.environ.get('USER'),
    home=os.environ.get('HOME')
)


def main():
    """ Main function.
    """
    args = _validate_args(_parser())

    if args['mode'] == 'rem':
        title_for_sbatch = 'pippopluto_title'
    else:
        title_for_sbatch = args['title']

    sbatch_script = sbatch(title=title_for_sbatch,
                           mem=args['mem'],
                           task_per_node=args['processors'],
                           executable=args['dftb_exe'],
                           user=config['username'])

    if args['bias']:
        if args['is_unix']:
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
    if args['is_unix']:
        dftbpI.add_keyword('Driver_File', args['address'])
    else:
        dftbpI.add_keyword('Driver_Host', args['address'])
        dftbpI.add_keyword('Driver_Port', args['port_dftb'])
    if not args['ddmc']:
        dftbpI.add_keyword('Hamiltonian_Dispersion_', 'LennardJones')
        dftbpI.add_keyword('Hamiltonian_Dispersion_Parameters','UFFParameters{}')
    else:
        dftbpI.add_keyword('Hamiltonian_Dispersion', 'dDMC {}')

    dftbpI.set_preset(args['dftb_type'])

    with open('dftb_in.hsd', 'w') as dftbf:
        dftbf.write(dftbpI.write())

    # Write data to the ipi input
    ipiI = ipi.InputIpi()
    for k, v in args.items():
        if k not in ['title', 'ddmc', 'mem', 'processors', 'dftb_type']:
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

    all_options = {}
    for k, v in args.items():
        all_options[k] = v

    dependancies = {}
    dependancies['group'] = {}
    dependancies['mandatory'] = ['is_unix', 'mode', 'timestep',
                                 'nstep', 'slots',
                                 'initial_temperature', 'timeout', 'dftb_type',
                                 'dftb_exe', 'ddmc', 'processors', 'mem', 'xyzfile']
    dependancies['optional'] = ['port_dftb', 'title']
    dependancies['group']['mode:rem'] = ['Tmax', 'Tmin', 'nrep', 'rstride', 'steep']
    dependancies['group']['mode:md'] = ['temperature']
    dependancies['group']['bias:True'] = ['port_bias']
    dependancies['group']['is_unix:True'] = ['address_dftb', 'address_bias']

    return _check_dependancy(dependancies, all_options)
    

def _not_none(in_var, in_dict):
    if in_dict[in_var] == None:
        raise(ValueError('You must specify a value for {:}'.format(in_var)))

def _check_value(string, in_dict):
    if string.find('port') >= 0:
        port = in_dict[string]
        if port is not None and not portsMaster.is_port_free(port):
            raise(ValueError('The port choosen ({:}) for {:} is not available.\
            Do not specify any port!'.format(port, string)))
        else:
            in_dict[string] = portsMaster.giveme_a_port()

    elif string == 'title':
        if in_dict[string] == None:
            in_dict[string] = in_dict['xyzfile']

    elif string == 'is_unix':
        if in_dict[string] and in_dict['address'] is None:
            in_dict['address'] = str(in_dict['title']) + '_' + str(config['username'])
            counter = 0         # To be sure the address is unique
            address = in_dict['address']
            while os.path.isfile(in_dict['address']):
                in_dict['address'] = address+'_'+str(counter)
                counter += 1
        else:
            _not_none(string, in_dict)
            
    else:
        _not_none(string, in_dict)

    return in_dict

        

def _check_dependancy(dep_dict, opt_dict):

    for k in dep_dict.keys():
        if k == 'mandatory':
            for __v in dep_dict[k]:
                _not_none(__v, opt_dict)

    for k in dep_dict.keys():
        if k == 'optional':
            for __v in dep_dict[k]:
                _check_value(__v, opt_dict)
                print('OPTIONAL: ', k, __v, opt_dict[__v])

    for k in dep_dict.keys():
        if k == 'group':
            for k_1 in dep_dict[k].keys():
                key, opt = k_1.split(':')
                if str(opt_dict[key]) == opt:
                    for __v in dep_dict[k][k_1]:
                        _check_value(__v, opt_dict)

    print(opt_dict)
    print('port_dftb', opt_dict['port_dftb'])
    return opt_dict


def _ispositive(number):
    """Simply return is a number is positive.
    """
    return number > 0


def _parser():
    """Parse the arguments from command line.
    """

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

    rem.add_argument('--bias',
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
                                           'Parameters to initialize the \
                                           system')
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
    ffsocket.add_argument('--port_dftb',
                          action='store',
                          default=None,
                          type=int,
                          help='Port used by the socket. Leave it and I will try to find one')
    ffsocket.add_argument('--port_bias',
                          action='store',
                          default=None,
                          type=int,
                          help='Port used by the socket when bias is required. Leave it and I will try to find one')
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
                          dest='is_unix',
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
                        version='%(prog)s ' + str(GIT_V, encoding='UTF-8'))


    return vars(parser.parse_args())

if __name__ == '__main__':
    main()
