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
import sys, os, glob
import scipy
from scipy.interpolate import RectBivariateSpline
import numpy as np
from PIL import Image
import pandas as pd



## configuration / plot parameters

FOV_UNITS = "muas"  # can be set to "muas" or "M" (case sensitive)

## EVPA_CONV not yet implemented! this will only work for observer convention!
EVPA_CONV = "EofN"  # can be set fo "EofN" or "NofW" 



## no need to touch anything below this line

def colorbar(mappable):
  """ the way matplotlib colorbar should have been implemented """
  from mpl_toolkits.axes_grid1 import make_axes_locatable
  ax = mappable.axes
  fig = ax.figure
  divider = make_axes_locatable(ax)
  cax = divider.append_axes("right", size="5%", pad=0.05)
  return fig.colorbar(mappable, cax=cax)

if __name__ == "__main__":

   #for one file, uncomment: fname = sys.argv[-1]
  #fname = sys.argv[-1]
  #for multiple files, - uncomment: files = np.sort(glob... AND for loop AND if fname[..]
  print(sys.argv[1])
  files = np.sort(glob.glob(os.path.join(sys.argv[1],'*.h5')))
  
  first = False
  curves = []
  for fname in files:
    #print(fname)
    if fname[-3:] != ".h5": continue
    print("plotting {0:s}".format(fname))

    # load
    hfp = h5py.File(fname,'r')    
    dx = hfp['header']['camera']['dx'][()]
    print('dx = ', dx)
    print('M_Unit = ', hfp['header']['units']['M_unit'][()])
    dsource = hfp['header']['dsource'][()]
    lunit = hfp['header']['units']['L_unit'][()]
    fov_muas = dx / dsource * lunit * 2.06265e11
    scale = hfp['header']['scale'][()]
    evpa_0 = 'W'
    if 'evpa_0' in hfp['header']:
      evpa_0 = hfp['header']['evpa_0'][()]
    #unpol = np.copy(hfp['unpol']).transpose((1,0))
    imagep = np.copy(hfp['pol']).transpose((1,0,2))
    I = imagep[:,:,0]
    #I = unpol
    #Q = imagep[:,:,1]
    #U = imagep[:,:,2]
    #V = imagep[:,:,3]
    hfp.close()

    # set extent (assumption of square image)
    if FOV_UNITS == "muas":
      extent = [ -fov_muas/2, fov_muas/2, -fov_muas/2, fov_muas/2 ]
    elif FOV_UNITS == "M":
      extent = [ -dx/2, dx/2, -dx/2, dx/2 ]
    else:
      print("! unrecognized units for FOV {0:s}. quitting.".format(FOV_UNITS))


    # get mask for total intensity based on negative values
    Imaskval = np.abs(I.min()) * 100.
    Imaskval = np.nanmax(I) / np.power(I.shape[0],5.)

    # command line output
    print("Flux [Jy]:    {0:g} {1:g}".format(I.sum()*scale, imagep.sum()*scale))
    #print("Flux [Jy]:    {0:g} {1:g}".format(I.sum()*scale, unpol.sum()*scale))
    print("I [Jy]: {0:g} ".format(I.sum()*scale))

    #STOKES I UNPOL 
    z = I
    '''
    plt.figure(figsize=(4,4))
    vmax = z.max() / np.sqrt(1.5)
    im1 = plt.imshow(z, cmap='afmhot', vmin=0., vmax=vmax, origin='lower', extent=extent)
    colorbar(im1)
    plt.savefig(fname.replace(".h5",".Stokes_I_.png"))
    ax_list = im1.axes
    #print(ax_list.viewLim)
    '''
    
    print("I old shape = ", z.shape)
    x, y = np.meshgrid(np.linspace(-z.shape[0]/2, z.shape[0]/2, z.shape[0]), np.linspace(-z.shape[0]/2, z.shape[0]/2, z.shape[0]))
    #print(x.shape)
    #print(y.shape)
    
    f = scipy.interpolate.RectBivariateSpline(x[0,:], y[:,0], z)
    

    #STOKES I INTERPOLATED
    #plt.figure(figsize=(4,4))
    # n is the x axis, so in the default case it's 160. If it's 160, we want the interpolated mesh to be finer by say 60 points (nAdd). (finer by 37.5%)
    # If the IPOLE produced original mesh is finer, so the x axis is say 400, we want the interpolated mesh to be finer by say 150 points and so on (nAdd).
    n = z.shape[0]
    nAdd = round(z.shape[0] * 0.375)
  
    xnew, ynew = np.meshgrid(np.linspace(-z.shape[0]/2, z.shape[0]/2, z.shape[0] + nAdd), np.linspace(-z.shape[0]/2, z.shape[0]/2, z.shape[0] + nAdd), indexing="ij")
    #print(xnew.shape)
    #print(ynew.shape)
    znew = f(xnew, ynew, grid=False)
    print("I new shape = ", znew.shape)
    
    '''
    vmax =znew.max()/np.sqrt(1.5)
    im2 = plt.imshow(znew, cmap='afmhot',vmin=0., vmax =vmax, origin='lower', extent=extent)
    colorbar(im2)
    plt.savefig(fname.replace(".h5",".Stokes_I_interpolated.png"))
    '''
    
    if not first:
        # Code to execute only for the first element
        first = True
        xnewScaled=xnew * (160/n)
        #print(znew.shape[0])
        #print(n)
        #print(xnewScaled)
        ynewScaled=ynew * (160/n)
        curves.append(xnewScaled[:,0])
        curves.append(ynewScaled[0,:])
        
    line0 = znew[int(znew.shape[0]/2),:]
    curves.append(line0)
    #print(line0)

    #line0 = znew[110,:]
    #curves.append(line0)

    line180 = znew[:,int(znew.shape[0]/2)]
    curves.append(line180)

    
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 2, 1)
    ax2 = fig.add_subplot(1, 2, 2)
    ax1.imshow(z, cmap='afmhot', origin='lower', extent=extent)
    ax2.imshow(znew, cmap='afmhot', origin='lower', extent=extent)
    ax2.axvline(x = 0, color='yellow',ls='--')
    ax2.axhline(y = 0, color='yellow', linestyle='--')
    plt.savefig(fname.replace(".h5","_compare_interpolation.png"))
    plt.close()
    
  
  df = pd.DataFrame(curves)
  print(sys.argv[1])
  #print(os.path.join(sys.argv[1],'interpolated_curves_centres_'+str(sys.argv[0].split('/')[-3])+'_file.csv'))
  df.to_csv(os.path.join(sys.argv[1],'interpolated_curves_centres_'+str(sys.argv[1].split('/')[-3])+'_file.csv'), index=False)
