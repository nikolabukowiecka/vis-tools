# Written by Richard Qiu
# July 2021
# Modified by Angelo Ricarte
# January 2022

from itertools import product
import os
from sys import argv
import time
import numpy as np
import pickle
from scipy import optimize, stats
from helpers import run_ipole, log, get_dump_paths, StopMinEarly

####################
##THINGS TO CHANGE##
####################

source = 'M87'               #M87 or SgrA
N_DUMPS = 100                #>= 2
MIN_T = 10_000               #Minimum time in M to start fitting
MAX_T = None                 #If none, goes to the end of the simulation.
x0 = [np.log(1e24), 8]       #Your best guess for natural log of Munit and the slope.  Better to undershoot than overshoot the guess.
EXE = "/work/pi_gkhanna_uri_edu/Nikola/ipole/ipole"   #Your executable version of IPOLE.
do_variable_kappa = False     #If set to True, appropriate keywords are sent to ipole.

# Output directories.
log_dir_base = "/project/u2grc/Nikola/ipole/mfitting_test"
Munit_table = "/project/u2grc/Nikola/ipole/mfitting_test/mfittingTables.txt"

# I created a pickle file to determine dump paths.  If you don't have one, set pickleFile to None, and specify dumps_dir.
# The script should function normally, just slightly slower near the beginning.
pickleFile = None
dumps_dir = "/project/u2grc/Nikola/newSimulations/KerrLow"

# Folders (within dumps_dir) for which Munit is computed.  
# Magnetic field state and spin are read from these names in interpretFolderName() below, so change that if necessary.
folders = [
	 "KerrLow"
	 #"KerrMid"
	 #"analysis_ipole_a.3",
	 #"analysis_ipole_a.5",
	 #"analysis_ipole_a.7",
	 #"analysis_ipole_a.9",
	 #"analysis_ipole_am.3",
	 #"analysis_ipole_am.5",
	 #"analysis_ipole_am.7",
	 #"analysis_ipole_am.9",
	 #"analysis_ipole_SANE_a0",
	 #"analysis_ipole_SANE_a.3",
	 #"analysis_ipole_SANE_a.5",
	 #"analysis_ipole_SANE_a.7",
	 #"analysis_ipole_SANE_a.9",
	 #"analysis_ipole_SANE_am.3",
	 #"analysis_ipole_SANE_am.5",
	 #"analysis_ipole_SANE_am.7",
	 #"analysis_ipole_SANE_am.9",
]

# Combinations of Rlow and Rhigh to fit.
Rlowhighs = [
	 #(1.0, 1.0),
	 #(1.0, 10.0),
	# (1.0, 20.0),
	 (1.0, 40.0)
	# (1.0, 80.0),
	# (1.0, 160.0),
]

##############################################
##CHANGEABLE, BUT YOU PROBABLY DON'T WANT TO##
##############################################

OBJ_STOP_THRESHOLD = 1e-5  # If the "loss function" falls below this threshold, stop.
freqs = [230e9]            # Frequency at which fluxes are computed.

if source == 'SgrA':
	TARGET_FLUX = 2.4 # Sgr A*
	inclinations = [
		10.0,
		30.0,
		50.0,
		70.0,
		90.0,
		110.0,
		130.0,
		150.0,
		170.0,
	]
elif source == 'M87':
	TARGET_FLUX = 0.5 # M87*
	inclinations = [163]

# Finally, produce a list of parameter combinations.
params = list(product(folders, Rlowhighs, inclinations, freqs))
# e.g.,
# params = [
#	 ["A_a.9_1e-5", (1.0, 20.0), 10.0, 230e9],
#	 ["A_am.9_1e-5", (1.0, 20.0), 90.0, 230e9],
# ]

def compute_flux_array(ts, a, b, Rlow, Rhigh, inc, freq, log_out_path="log.txt", data_log_path="fit_iters_data.txt"):
	"""
	Function to call ipole over a range of times, logs results out. 
	Computes Munits given log-linear model parameters. Explicitly:
	munit = exp(a + b * t / 1e6)
	where the 1e6 scaling of b required for the opimization routine
	"""

	#Caution:  global variables.
	global iter, time_dump_dict
	print(dump_paths)   
	log("call ipole", log_out_path)
	args = []
	fluxes = []
	for t in ts:
		munit = np.exp(a + b * t / 1e6)
		print("Munit (initial guess)= ", munit)
		fluxes.append(run_ipole(munit, args, time_dump_dict[t], Rlow, Rhigh, inc, freq, source=source, EXE=EXE, do_variable_kappa=do_variable_kappa))
	log(f"{time.time()} {a} {b} " + " ".join(str(x) for x in fluxes), data_log_path)
	log("{0:g} {1:g} {2:g}".format(munit, a, b), log_out_path)
	return np.array(fluxes)

def loss_func_unitless(x, ts, Rlow, Rhigh, inc, freq, log_out_path, data_log_path):
	"""
	Minimizes loss function of the form (fractional deviation in flux)**2 + (fractional change in flux over the time interval)**2

	Stops optimization routine early if loss is below OBJ_STOP_THRESHOLD
	"""

	#Perform a change of variables to ensure that the pivot point of the slope is the center of the time series.
	#This helps ensure independence of a and b.
	DeltaT = np.max(ts) - np.min(ts)
	a = x[0] - x[1] * (DeltaT/1e6/2)
	b = x[1]

	#Evaluate fluxes.  Define loss function.
	fluxes = compute_flux_array(ts, a, b, Rlow, Rhigh, inc, freq, log_out_path, data_log_path)
	slope = stats.linregress(ts, fluxes).slope
	meanFlux = np.mean(fluxes)
	loss = (0.5*(meanFlux - TARGET_FLUX)/TARGET_FLUX)**2 + (0.5*(meanFlux - TARGET_FLUX)/meanFlux)**2 + (slope * DeltaT / meanFlux)**2

	if loss < OBJ_STOP_THRESHOLD:
		raise StopMinEarly(x, loss)
	return loss

def interpretFolderName(folderName):
	"""
	Assuming a particular way that the folder is named, then reading magnetic field state and spin.
	Change this function if your conventions are different.
	"""
	Bstate = 'MAD'
	#spin = 0.1
	#spin = 0.5
	if 'Low' in folderName:
		spin = 0.1
	if 'Mid' in folderName:
		spin = 0.5
	
	(spin)
	#spin = float(folder.split('_')[-1][1:].replace('m','-'))
	#if 'SANE' in folder:
	#	Bstate = 'SANE'
	#else:
	#	Bstate = 'MAD'
    
    #folder.split('_')[-1][1:].replace('m','-')
    
	return Bstate, spin

def constructSimplex(x0, del_a=1, del_b=3):
	"""
	For the fitting routine.  From the best guess, construct a triangle with reasonable step sizes for our problem.
	"""

	v1 = x0
	v2 = [x0[0]-del_a, x0[1]-del_b]
	v3 = [x0[0]-del_a, x0[1]+del_b]
	return np.array([v1, v2, v3])

if __name__ == "__main__":
	global time_dump_dict
	start_time = time.time()

	#In a wrapper script, this integer tells you which combination for this particular job to do.
	iter = int(argv[1])
	if iter == -1:
		print(len(params))
		quit()
	folder, (Rlow, Rhigh), inc, freq = params[iter]

	#Inferring the spin and magnetic field state from the folder name.  Change this function if your conventions are different.
	Bstate, spin = interpretFolderName(folder)

	#Flip retrogrades.
	if (source == 'M87') & (spin < 0):
		inc = 180.0 - inc

	#Combination now established.  Print.
	print(f"{Bstate} {spin} {Rlow} {Rhigh} {inc}")

	if pickleFile is not None:
		with open(pickleFile, 'rb') as openFile:
			pickledDictionary = pickle.load(openFile)
		dumps_dir = pickledDictionary['startingDirectory'] + folder + '/'
	elif dumps_dir is None:
		raise ValueError("Either set pickleFile or dumps_dir to tell the algorithm where the files are.")
	
	#Logs are organized in a series of nested folers.  Set this up.
	log_dir = os.path.join(log_dir_base, f"{folder}/Rlow{Rlow}_Rhigh{Rhigh}/inc{inc}/freq{freq/1e9:3.2f}/")
	log_out_path = os.path.join(log_dir, f"log.txt")
	os.makedirs(log_dir, exist_ok=True)
	[os.remove(file.path) for file in os.scandir(log_dir)]
	data_out_path = os.path.join(log_dir, f"fit_iters_data.txt")

	#Try to open the Munit_table and search for existing entries.
	if os.path.isfile(Munit_table):
		#Search for existing entries.
		existingTable = np.loadtxt(Munit_table, dtype=str)
		existingCombos = [(existingTable[row,0], existingTable[row,1], existingTable[row,2], existingTable[row,3], existingTable[row,4]) for row in range(existingTable.shape[0])]
		thisCombo = (Bstate, str(spin), str(Rlow), str(Rhigh), str(inc))
		if thisCombo in existingCombos:
			print(f"...is already computed.  Skipping.")
			quit()
	else:
		log("#Bstate spin Rlow Rhigh Inclination Munit_a Munit_b fitting_score", Munit_table)

	#Get a list of files to fit.
	dump_paths, times = get_dump_paths(dumps_dir, N_DUMPS, MIN_T, MAX_T, pickleFile=pickleFile)
	time_dump_dict = dict(zip(times, dump_paths))
	log("timestamp a b " + " ".join(os.path.basename(dump_path) for dump_path in dump_paths), data_out_path)
	log("timestamp a b " + " ".join(str(t) for t in times), data_out_path)
	
	try: 
		# This is where the fitting happens!
		simplex = constructSimplex(x0)
		opt_result = optimize.minimize(
			loss_func_unitless,
			x0=x0,
			args=(times, Rlow, Rhigh, inc, freq, log_out_path, data_out_path),
			 method='Nelder-Mead', options={'disp': True, 'initial_simplex': simplex, 'xatol': 0.01, 'fatol': 0.001},
		)
		(a_prime, b), loss = opt_result.x, opt_result.fun
	except StopMinEarly as err:
		(a_prime, b), loss = err.x, err.loss

	#Redefined 'a' in a way that should make it more independent of b to help with fitting.  Before saving, switch back.
	a = a_prime - b * (np.max(times) - np.min(times))/1e6/2

	#Save values to files.
	log(f"(a, b) found: {(a, b)}", log_out_path)
	log(f"final loss: {loss}", log_out_path)
	lineToSave = f"{Bstate} {spin} {Rlow} {Rhigh} {inc} {a} {b} {loss}"
	log(lineToSave, Munit_table)
	print("time elapsed (s):", time.time() - start_time)
