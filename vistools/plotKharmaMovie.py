import pyharm
import pyharm.plots.plot_dumps as pplt
import matplotlib.pyplot as plt
import numpy as np
#import ffmpeg
from folderToMovie import *
import glob
import os
from matplotlib.colors import LogNorm

def ppp():
    print('y')


def colorbar(mappable):
	""" the way matplotlib colorbar should have been implemented """
	from mpl_toolkits.axes_grid1 import make_axes_locatable
	ax = mappable.axes
	fig = ax.figure
	divider = make_axes_locatable(ax)
	cax = divider.append_axes("right", size="5%", pad=0.05)
	return fig.colorbar(mappable, cax=cax)

def assembleFiles(startingDirectory):
	
	allFiles = glob.glob(os.path.join(startingDirectory,"*phdf"))
	orderingStrings = [file.split('/')[-1].split('.')[2] for file in allFiles]
	orderingIntegers = []
	for string in orderingStrings:
		try:
			orderingIntegers.append(float(string))
		except:
			if string == 'final':
				orderingIntegers.append(np.inf)
	return np.array(allFiles)[np.argsort(orderingIntegers)]

def plotKharmaFrame(filename, output=None, key='rho', cmap='turbo', dynamicRange=4, norm=None, phi_slice=None):

	dump = pyharm.load_dump(filename)
	time = dump['t']
 
	if phi_slice is None:
		#Perform an azimuthal average
		data = np.transpose(np.mean(dump[key][...], axis=-1))
	else:
		data = np.transpose(dump[key][:,:,phi_slice])

	r, th = dump.grid.get_xz_locations(mesh=True, native=True)
	#For now, just plotting in native coordinates.
	fig, ax = plt.subplots(1, 1, figsize=(5,4))
	
	if norm is None:
		norm = LogNorm(vmax=np.max(data), vmin=np.max(data)/10**dynamicRange)
	image = ax.pcolormesh(r.transpose(), th.transpose(), data, cmap=cmap, norm=norm)
	ax.set_xlabel('X1', fontsize=12)
	ax.set_ylabel('X2', fontsize=12)
	ax.text(0.95, 0.05, f"$t={time:4.0f}$", fontsize=12, color='white', transform=ax.transAxes, ha='right', va='bottom')
	colorbar(image)
	
	fig.tight_layout()
	if output is None:
		fig.show()
	else:
		fig.savefig(output, dpi=400)
		plt.close(fig)

def plotKharmaFrame_xz(filename, output=None, key='log_rho', cmap='turbo', vmin=-4, vmax=1.5, window=(-20,20,-20,20)):

    dump = pyharm.load_dump(filename)
    time = dump['t']

    fig, ax = plt.subplots(1, 1, figsize=(5,4))
    pplt.plot_xz(ax, dump, key, vmin=vmin, vmax=vmax, window=window)

    #Oops, this only works in x-z.
    #pplt.overlay_field(ax, dump, nlines=50)
    ax.text(0.95, 0.05, f"$t={time:4.0f}$", fontsize=12, color='k', transform=ax.transAxes, ha='right', va='bottom')

    ax.set_xticks(np.linspace(window[0], window[1], 5))
    ax.set_yticks(np.linspace(window[2], window[3], 5))

    fig.tight_layout()
    if output is None:
        fig.show()
    else:
        fig.savefig(output, dpi=400)
        plt.close(fig)
    plt.close(fig)
    
def plotKharmaFrame_xy(filename, output=None, key='log_rho', cmap='turbo', vmin=-4, vmax=1.5, window=(-20,20,-20,20)):

	dump = pyharm.load_dump(filename)
	time = dump['t']

	fig, ax = plt.subplots(1, 1, figsize=(5,4))

	pplt.plot_xz(ax, dump, key, vmin=vmin, vmax=vmax, window=window)
	pplt.overlay_field(ax, dump)
	ax.text(0.95, 0.05, f"$t={time:4.0f}$", fontsize=12, color='k', transform=ax.transAxes, ha='right', va='bottom')

	ax.set_xticks(np.linspace(window[0], window[1], 5))
	ax.set_yticks(np.linspace(window[2], window[3], 5))

	fig.tight_layout()
	if output is None:
		fig.show()
	else:
		fig.savefig(output, dpi=400)
		plt.close(fig)

def plotKharmaMovie(startingDirectory, movieName, temporaryFolderName='/images/frames/', **kwargs):
    #plotKharmaFrame_xz('/Users/nikolabukowiecka/Desktop/Nikola/BHI collab/KHARMA output/mad/torus.out0.00000.phdf', output='frame1.png')
    #os.system("rm "+os.path.join(temporaryFolderName, "*.png"))
    #print(os.path.join(temporaryFolderName))
#    allFiles = assembleFiles(startingDirectory)
#    for frameNumber in range(len(allFiles)):
#        print(frameNumber)
#        try:
#            plotKharmaFrame_xy(allFiles[frameNumber], output=os.path.join(startingDirectory,"frame{0:04}.png".format(frameNumber)), **kwargs)
#        except:
#            print(f"Could not read {allFiles[frameNumber]}.  Something went wrong.")
#            continue

    folderToMovie(startingDirectory, movieName)
    print(f"Saved to {movieName}.")

if __name__ == '__main__':
	#Movie
	'''
	startingDirectory = '/n/holyscratch01/narayan/aricarte/kharma_output/mad_gpu_quad_highres_betamin30'
	movieName = '../movies/' + startingDirectory.split('/')[-1] + '.mp4'
	plotKharmaMovie(startingDirectory, movieName)

	startingDirectory = '/n/holyscratch01/narayan/aricarte/kharma_output/mad_gpu_quad_highres_betamin300'
	movieName = '../movies/' + startingDirectory.split('/')[-1] + '.mp4'
	plotKharmaMovie(startingDirectory, movieName)
	'''
	
	'''/
	startingDirectory = '/n/holyscratch01/narayan/aricarte/kharma_output/mad_gpu_quad_abs'
	movieName = '../movies/' + startingDirectory.split('/')[-1] + '.mp4'
	plotKharmaMovie(startingDirectory, movieName)
	'''
print("Directory: /project/pi_dgobeille_uri_edu/Nikola/...")
dir = input()
startingDirectory = '/project/pi_dgobeille_uri_edu/Nikola/{}'.format(dir)
#startingDirectory = '/work/pi_dgobeille_uri_edu/Nikola/kharma'
#startingDirectory = '/project/pi_dgobeille_uri_edu/Nikola/{}'
print("Movie name: ")
mov = input()
#movieName = '../movies/' + startingDirectory.split('/')[-1] + '.mp4'
#movieName = startingDirectory.split('/')[-1] + '.mp4'
movieName = '{}.mp4'.format(mov)
plotKharmaMovie(startingDirectory, movieName)

	#One plot, for testing
	#dumpFile = '/n/holyscratch01/narayan/aricarte/kharma_output/mad_gpu_quad_abs/torus.out0.02500.phdf'
#dumpFile = '/Users/nikolabukowiecka/Desktop/Nikola/BHI collab/KHARMA output/mad/torus.out0.00000.phdf'
	#dumpFile = '/n/holyscratch01/narayan/aricarte/kharma_output/mad_gpu_quad_abs/torus.out0.02518.phdf'
	#dumpFile = '/n/holyscratch01/narayan/aricarte/kharma_output/mad_gpu_dip_highres/torus.out0.00332.phdf'
	#plotKharmaFrame_xz(dumpFile, key='log_sigma', vmin=-4, vmax=1.5)
	#plotKharmaFrame_xz(dumpFile, key='log_Thetae', vmin=-3, vmax=0)
	#plotKharmaFrame_xz(dumpFile, key='b^r', vmin=-1e-10, vmax=1e-10)
#print('kk')
#plotKharmaFrame_xz(dumpFile, key='log_rho', vmin=-4, vmax=1.5)
#plotKharmaFrame_xz('/Users/nikolabukowiecka/Desktop/Nikola/BHI collab/KHARMA output/mad/torus.out0.00000.phdf', output='frame1.png')
#print('kk2')
