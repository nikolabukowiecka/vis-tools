# Written by Richard Qiu
# July 2021
# Modified by Angelo Ricarte
# January 2022

import glob
import os
import subprocess
import h5py
import numpy as np
import pickle
import pdb

def run_ipole(munit, args, dumpfile, Rlow, Rhigh, inc, freq, res=100, outfile=None, source='SgrA', unpol=False, EXE="/n/home11/aricarte/projects/eht/ipole_versions/ipole_dev_narayan/ipole", \
	do_variable_kappa=False):
	"""
	Run ipole on an image with particular keywords.  Return the total flux.
	"""
	mut = "--M_unit={0:g}".format(munit)
	args = [f"--thetacam={inc}", f"--dump={dumpfile}", "--nx={0:d}".format(res), "--ny={0:d}".format(res), mut, f"--trat_small={Rlow}", f"--trat_large={Rhigh}", *args]
	if source == 'SgrA':
		args = [EXE, "--MBH=4.14e6", f"--freqcgs={freq}", "--dsource=8.127e3", "--fov=200.0", *args] # Sgr A*
	elif source == 'M87':
		args = [EXE, "--MBH=6.5e9", f"--freqcgs={freq}", "--dsource=16.9e6", "--fov=160.0", *args] # M87*
	else:
		raise ValueError("Value for 'source' kwarg not supported.  Set equal to either SgrA or M87.")
	if unpol:
		args.append("-unpol")
	if outfile is None: 
		args.append("-quench")
	else:
		args.append(f"--outfile={outfile}")
	if do_variable_kappa:
		args.append(f"--variable_kappa=1")
		args.append(f"--emission_type=2")

	print(" ".join(args))
	#pdb.set_trace()
	#os.system(" ".join(args))
	proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	output = [ z for y in [ str(x)[2:-1].split("\\n") for x in proc.communicate() ] for z in y ]

	#Read flux directly out of the terminal output.  Hopefully the ipole devs don't change these messages!
	Ftot_line = [l for l in output if 'unpol xfer' in l][0]
	print(Ftot_line)
	st = Ftot_line.split()
	if unpol:
		#A couple words before, with a parenthesis to get rid of.
		flux = float(st[-2+st.index('unpol')][1:])
	else:
		#Four words before, with no parenthesis.
		flux = float(st[-4+st.index('unpol')])
	print(flux)
	return flux

def log(s, log_file="log.txt"):
	"""
	Print and save a line to a file.
	"""
	print(s)
	fp = open(log_file, 'a')
	fp.write(s + "\n")
	fp.close()

def get_dump_paths_fast(base_dir, pickleFile, n_dumps=100, min_t=10_000, max_t=None):
	"""
	Get dump files evenly spaced in time from a pre-processed file.
	"""

	#Read values from a pickled dictionary.
	with open(pickleFile, 'rb') as myfile:
		dictionary = pickle.load(myfile)
	subdictionary = dictionary['subdirectories'][base_dir.split('/')[-2]]
	dump_paths = np.array([base_dir + name for name in subdictionary['filename']])
	times = subdictionary['time']

	#Find matches.
	max_t = times.max() if max_t is None else max_t
	target_times = np.linspace(min_t, max_t, n_dumps)
	dump_idx = np.searchsorted(times, target_times)
	print(times)
	print(target_times)
	return list(np.array(dump_paths)[dump_idx]), list(times[dump_idx])

def get_dump_paths_slow(base_dir, n_dumps=100, min_t=10_000, max_t=None):
    """
    Get dump files evenly spaced in time by opening them one by one.
    """
    dump_paths = sorted(glob.glob(os.path.join(base_dir, "*.h5")))
    times = []
    #pdb.set_trace()	
    for dump_path in dump_paths:
        with h5py.File(dump_path, "r") as f:
            times.append(f["t"][()])
    times = np.array(times)
    max_t = times.max() if max_t is None else max_t
    target_times = np.linspace(min_t, max_t, n_dumps)
    dump_idx = np.searchsorted(times, target_times)
    print(times)
    print(target_times)
    return list(np.array(dump_paths)[dump_idx]), list(times[dump_idx])

def get_dump_paths(base_dir, n_dumps=100, min_t=10_000, max_t=None, pickleFile=None):
	"""
	Read from pickleFile if provided; otherwise get via opening files one by one in the base_dir.
	"""

	if pickleFile is None:
		return get_dump_paths_slow(base_dir, n_dumps=n_dumps, min_t=min_t, max_t=max_t)
	else:
		return get_dump_paths_fast(base_dir, pickleFile, n_dumps=n_dumps, min_t=min_t, max_t=max_t)

# from https://redman.xyz/doku.php/gsoc:scipy_minimize_value_threshold
class StopMinEarly(Exception):
	def __init__(self, x, loss):
		self.x = x
		self.loss = loss
