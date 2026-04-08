import matplotlib.pyplot as plt
import numpy as np
import h5py
import sys
import os
import glob
import argparse
from folderToMovie import *

parser = argparse.ArgumentParser(description='Convert .h5 images to .png')
    
parser.add_argument('pathInput', type = str, help = 'Type in the ipole images: ')
args = parser.parse_args()

startingDirectory = args.pathInput

allFiles = glob.glob(os.path.join(startingDirectory,"*h5"))

for file in allFiles:
    #print(file)
    #print(file.split('.')[-2]+"_png")

    # load image data (unpolarized intensity and scaling factors) from hdf5 image
    hfp = h5py.File(file,'r')
    dx_cgs = hfp['header']['camera']['dx'][()] * hfp['header']['units']['L_unit'][()]
    fovMuas = dx_cgs / hfp['header']['dsource'][()] * 2.06265e11
    cgsToJy = hfp['header']['scale'][()]
    unpol = np.copy(hfp['unpol']).transpose((1,0)) * cgsToJy
    hfp.close()

    # make plot and show
    ext = [ -fovMuas/2, fovMuas/2, -fovMuas/2, fovMuas/2 ]
    plt.imshow(unpol, origin='lower', extent=ext)
    plt.savefig(file.split('.')[-2])
    plt.show()
    
    #movieName = '{}.mp4'.format(startingDirectory.split('/')[4])
    #folderToMovie(startingDirectory, movieName)
    #print(f"Saved to {movieName}.")
    