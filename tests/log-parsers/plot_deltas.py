#!/usr/bin/env python3
#
# Plotting script for the smi-enumeration test output file.
#
# 1. Execute a test run on the smi-enumeration-test branch:
#    $ sudo python3 chipsec_main.py -m tools.smm.smm_ptr -a scan,0x5:0x5 -l output.log
# 2. Plot the result:
#    $ python3 process_histogram.py output.log
#

import sys
import pyjson5
import numpy as np
import matplotlib.pyplot as plt
import statistics
import argparse

def get_basename(filename):
    pos = filename.rfind('/') 
    if pos != -1:
        return filename[pos + 1:]
    else:
        return filename

def process(args):
    with open(args.filename, 'r') as f:
        time = 0
        start_offset_time = 0
        for line in f:
            if line.startswith("[*] Fuzzing SMI#"):
                ini = line.find("#") + 2
                fin = line[ini:].find("(") - 1
                smi = line[ini:ini+fin]
            elif line.startswith("Deltas:"):
                pos = line.find("{")
                info = pyjson5.loads(line[pos:])
                times = []
                init_time = 0
                curr_time = 0
                count = 0
                for i in info['times']:
                    if not init_time:
                        init_time = i
                    curr_time = i - init_time
                    times.append(curr_time/1e9)
                    #times.append(count)
                    count += 1
                print(f"SMI# {smi}: Average {sum(info['deltas'])/len(info['deltas'])} counts, Std Dev. {statistics.stdev(info['deltas'])} counts")
                plt.plot(times, info['deltas'])
                plt.xlabel('Time offset [s]')
                plt.ylabel('CPU counts')
                plt.gcf().suptitle(get_basename(args.filename), y=1)
                if not args.join:
                    plt.title(f'Duration of the SMI# {smi} over time')
                    plt.show()
                else:
                    plt.title(f'Duration of the SMIs over time')
                    plt.draw()
            else:
                continue
        if args.join:
            plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='plot_deltas.py',
                    description='Plot SMI duration times')
    parser.add_argument('filename')
    parser.add_argument('-j', '--join', action='store_true')
    args = parser.parse_args()
    process(args)
