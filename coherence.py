from __future__ import division
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from ConfigParser import ConfigParser
import scipy.signal as sig
import argparse
import re
import numpy as np
import library as lib


# Unpack the command line
def parse_command_line():
    """
    parse command line. use sensisble defaults
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("--ini-file", "-i",
                        help    = 'stamp-pem config file',
                        default = './stamp_pem_configs.ini',
                        dest    = 'stamp_pem_config_file',
                        type    = str)
    params = parser.parse_args()

    return params


# instantiate parser and read the config file
stamp_pem_configs = ConfigParser()
stamp_pem_configs.read(parse_command_line().stamp_pem_config_file)

# get [env] params
section = 'env'
channel_list_path = stamp_pem_configs.get(section, 'channel_list')
channel_list = ConfigParser()
channel_list.read(channel_list_path)
channel_subsystems = channel_list.sections()

# get [run] params
section = 'run'
ss_regex = re.compile('[\w:\-]+')
subsystems = ss_regex.findall(stamp_pem_configs.get(section, 'subsystems').lower())
subsystems = list(set([cs for cs in channel_subsystems for ss in subsystems
                       if ss in cs.lower()]))
DARM = stamp_pem_configs.get(section, 'DARM')
subsystems = [DARM] + subsystems
duration = stamp_pem_configs.getint(section, 'duration')
start_time = stamp_pem_configs.getint(section, 'start_time')

# collect all channels [chan, sample_rate, (un)safe, (un)clean]
channel_data = []
for ix, ss in enumerate(subsystems):
    ss_channels = [cs for cs in channel_list.get(ss,'channels').split('\n') if len(cs) > 1]
    for ss_chan in ss_channels:
        channel_data.append([x for x in ss_chan.split(' ') if len(x) > 1])
channel_data = np.array(channel_data)

# get the timeseries data. can fetch 400 channels at once
# we may have more channels than that, so we loop
print('Collecting data')
fs_up = min([int(x) for x in channel_data[:, 1]])
max_chans = 400
iters = int(channel_data.shape[0] / max_chans) + 1
ts = []
for i in range(iters):
    timeseries = lib.stream_data(channel_data[i * max_chans:(i + 1) * max_chans, 0],
                                 fs_up      = fs_up,
                                 duration   = duration,
                                 start_time = start_time)
    ts.append(timeseries)

timeseries = np.hstack(([np.array(ts[i]) for i in range(len(ts))]))

# calculate the coherences: abs(Pxy)**2/(Pxx*Pyy)
coherence_results = {}
for ix in range(1, timeseries.shape[1]):
    f, Cxy = sig.coherence(timeseries[:,0], timeseries[:,ix], fs=fs_up)
    df = f[1] - f[0]
    coherence_results[channel_data[ix, 0]] = Cxy


#########################################3
# Make some plots
#########################################3
# print('making plot')
# coh = []
# for chan in channel_data[1:, 0]:
#     coh.append(coherence_results[chan])
# coh = np.array(coh)
# for i in range(10):
#     plt.plot(coh[i, :], label='{}'.format(channel_data[i, 0]))
# plt.legend()
# plt.savefig('coherence.png')
# plt.close()
