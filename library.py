from __future__ import division
import nds2
import os
os.environ['NDS2_CLIENT_ALLOW_DATA_ON_TAPE'] = '1'
import scipy.signal as sig
import scipy.io as sio
import sys
import numpy as np


def stream_data(channels,
                duration   = 600,
                start_time = 0,
                fs_up      = 256,
                portNumber = 31200):

    nds_osx = ('/opt/local/Library/Frameworks/Python.framework/' +
               'Versions/2.7/lib/python2.7/site-packages/')
    nds_sandbox = '/usr/lib/python2.7/dist-packages/'

    if os.path.exists(nds_osx):
        sys.path.append(nds_osx)
    elif os.path.exists(nds_sandbox):
        sys.path.append(nds_sandbox)

    # Connect to the right server
    ifo = channels[0][:2]
    if ifo == 'L1':
        ndsServer = 'nds.ligo-la.caltech.edu'
    elif ifo == 'H1':
        ndsServer = 'nds.ligo-wa.caltech.edu'
    else:
        sys.exit("unknown IFO specified")

    # Setup connection to the NDS
    try:
        conn = nds2.connection(ndsServer, portNumber)
    except RuntimeError:
        alert('ERROR: Need to run `kinit albert.einstein` before nds2 '
              'can establish a connection', color='FAIL')
        sys.exit(1)

    # get data
    data = conn.fetch(start_time, start_time + duration, channels)
    data = np.array(data)

    # stack data and downsample
    vdata = []
    for k in range(len(channels)):
        fsdown = data[k].channel.sample_rate
        down_factor = int(fsdown // fs_up)

        fir_aa = sig.firwin(20 * down_factor + 1, 0.8 / down_factor,
                            window='blackmanharris')

        # Using fir_aa[1:-1] cuts off a leading and trailing zero
        downdata = sig.decimate(data[k].data, down_factor,
                                ftype = sig.dlti(fir_aa[1:-1], 1.0),
                                zero_phase = True)
        vdata.append(downdata)

    return np.array(vdata).T


class bcolors:
    HEADER = '\033[0;35m'
    OKBLUE = '\033[0;34m'
    OKGREEN = '\033[0;32m'
    WARNING = '\033[0;33m'
    FAIL = '\033[0;31m'
    ENDC = '\033[0m'
    UNDERLINE = '\033[4m'


def alert(message, color='HEADER'):
    """
    print out messages to stdout in color

    Parameters
    ----------
    message : `str`
        message to be displayed
    color : `str`
        ['HEADER', 'OKBLUE', 'OKGREEN', 'WARNING', 'FAIL', 'UNDERLINE']
    """

    if color == 'HEADER':
        print(bcolors.HEADER + message + bcolors.ENDC)

    elif color == 'OKBLUE':
        print(bcolors.OKBLUE + message + bcolors.ENDC)

    elif color == 'OKGREEN':
        print(bcolors.OKGREEN + message + bcolors.ENDC)

    elif color == 'WARNING':
        print(bcolors.WARNING + message + bcolors.ENDC)

    elif color == 'FAIL':
        print(bcolors.FAIL + message + bcolors.ENDC)

    elif color == 'ENDC':
        print(bcolors.ENDC + message + bcolors.ENDC)

    elif color == 'UNDERLINE':
        print(bcolors.UNDERLINE + message + bcolors.ENDC)

    else:
        print(message)

