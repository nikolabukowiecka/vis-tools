"""

  Makes images from hdf5 output of ipole.
  2019.07.10 gnw

$ python ipole_plot.py path/to/images/*h5

$ ffmpeg -framerate 8 -i dump%*.png -s:v 1280x720 -c:v libx264 -profile:v high -crf 20 -pix_fmt yuv420p out.mp4
"""

import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
import numpy as np
import h5py
import pandas as pd
import sys, glob, os
from folderToMovie import *


## configuration / plot parameters

FOV_UNITS = "muas"  # can be set to "muas" or "M" (case sensitive)

## EVPA_CONV not yet implemented! this will only work for observer convention!
EVPA_CONV = "EofN"  # can be set fo "EofN" or "NofW" 



if __name__ == "__main__":


  files = np.sort(glob.glob(os.path.join(sys.argv[1],'*.h5')))
  outDict = {'t':[], 'Mdot':[], 'MdotEdd':[]}
  for fname in files:
    print(sys.argv[1:])

    if fname[-3:] != ".h5": continue
    print("plotting {0:s}".format(fname))

    # load
    hfp = h5py.File(fname,'r')  
    t = hfp['header']['t'][()]
    mdot = hfp['Mdot'][()]
    mdotEdd = hfp['MdotEdd'][()]
    
    outDict['t'] = np.append(outDict['t'], t)
    outDict['Mdot'] = np.append(outDict['Mdot'], mdot)
    outDict['MdotEdd'] = np.append(outDict['MdotEdd'], mdotEdd)


  outDict['t'] = outDict['t'].flatten()
  outDict['Mdot'] = outDict['Mdot'].flatten()
  outDict['MdotEdd'] = outDict['MdotEdd'].flatten()

  df = pd.DataFrame(outDict)
  df.to_csv(str(sys.argv[1].split('/')[-3])+'_Edd_ratio'+'.csv', index=False)

  hfp.close()
