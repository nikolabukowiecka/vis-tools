import pyharm
import pyharm.plots.plot_dumps as pplt
import pyharm.ana.analyses
import matplotlib.pyplot as plt
import numpy as np
#import ffmpeg
from folderToMovie import *
import glob
import os
from matplotlib.colors import LogNorm
import argparse

#if: python3 plot.py /project/u2grc/Nikola/newSimulations/KerrLow/images 2 xz log_rho
# meaning if given a path to images with "2" it will plot a movie, but:
#if: python3 plot.py /project/u2grc/Nikola/newSimulations/KerrLow 2 xz log_rho
# meaning if given a path to .phdf with "2" it will first plot frames, then a movie

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
        plt.show()
    else:
        plt.show()
        fig.savefig(output, dpi=400)
        plt.close(fig)
    plt.close(fig)

def plotKharmaFrame_xyz(filename, frame, var, output=None, cmap='turbo', vmin=-4, vmax=1.5, window=(-20,20,-20,20)):
    
    dump = pyharm.load_dump(filename)
    
    #if frame == 'rad':
    #    out = {}
    #    result = pyharm.ana.analyses.r_profiles(dump, out, vars=('rho', 'Pg', 'u^r', 'u^3', 'u_3', 'b', 'inv_beta', 'Ptot'))
    
    time = dump['t']

    fig, ax = plt.subplots(1, 1, figsize=(5,4))
    if frame == 'xy':
        pplt.plot_xy(ax, dump, var, vmin=vmin, vmax=vmax, window=window)
    if frame == 'xz':
        #print("With overlay field lines? y/n")
        #lines = input()
        pplt.plot_xz(ax, dump, var, vmin=vmin, vmax=vmax, window=window)
        #if lines == 'y':
        #pplt.overlay_field(ax, dump, nlines=50) # This only works in x-z.
    
    ax.text(0.95, 0.05, f"$t={time:4.0f}$", fontsize=12, color='k', transform=ax.transAxes, ha='right', va='bottom')

    ax.set_xticks(np.linspace(window[0], window[1], 5))
    ax.set_yticks(np.linspace(window[2], window[3], 5))

    fig.tight_layout()
    if output is None:
        plt.show()
    else:
        #plt.show()
        fig.savefig(output, dpi=400)
        #fig.savefig(output + '/images/' + var, dpi=400)
        #plt.close(fig)
    plt.close(fig)

def plotKharmaFrame(startingDirectory, imageNumber, frame, var):

    allFiles = assembleFiles(startingDirectory)
    #plotKharmaFrame_xyz(allFiles[imageNumber], frame, var, output=None, cmap='turbo', vmin=-4, vmax=1.5, window=(-20,20,-20,20))
    #Specify output to save figure:
    plotKharmaFrame_xyz(allFiles[imageNumber], frame, var, output = startingDirectory + '/images/' + allFiles[imageNumber].split('/')[-1].split('.')[2] + '_' + var +'_' + frame)
    #keys: 'rho', 'Pg', 'u^r', 'u^3', 'u_3', 'b', 'inv_beta', 'Ptot', 'FM'.. + log_ before
def plotKharmaMovie(startingDirectory, movieName, frame, var):

    allFiles = assembleFiles(startingDirectory)
    for frameNumber in range(len(allFiles)):
        try:
            plotKharmaFrame_xyz(allFiles[frameNumber], frame, var, output=os.path.join(startingDirectory, "frame{0:04}.png".format(frameNumber)))
        except:
            print(f"Could not read {allFiles[frameNumber]}.  Something went wrong.")
            continue

    folderToMovie(startingDirectory, movieName)
    #print(f"Saved to {movieName}.")

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Plot a variable and save an image for a chosen pdhf file or create a movie for a chosen variable across all avaliable pdhf files.')
    
    parser.add_argument('pathInput', type = str, help = 'Type in the directory: ~/...')
    parser.add_argument('type', type = int, help = 'Type: image (1) or a movie (2)')
    parser.add_argument('frame', type = str, help = 'Type frame: xy or xz')
    parser.add_argument('var', type = str, help = 'Type variable (rho, Pg, u^r, u^3, u_3, b, beta, inv_beta, Ptot, FM, FE) (log_..):')
    
    parser.add_argument('-num', '--imageNumber', type = int, help = 'Type: pdhf file number')
    
    
    args = parser.parse_args()
    
    startingDirectory = args.pathInput
    
    
    if args.type == 1:
        outDir = os.path.join(startingDirectory, "images")
        isOutDir = os.path.isdir(outDir)
        if isOutDir == False:
            os.mkdir(outDir)
        plotKharmaFrame(startingDirectory, args.imageNumber, args.frame, args.var)
    elif args.type == 2:
        movieName = startingDirectory.split('/')[-1] + '_' + args.var + '.mp4'
        plotKharmaMovie(startingDirectory, movieName, args.frame, args.var)
        
    #FRAMES SHOULD BE DELETED IN BASH AFTER MOVIE CREATION!!
    
    '''
    #For me when I work locally, not on the cluster:
    startingDirectory = "/Users/nikolabukowiecka/Desktop/Nikola/BHIcollab/kharma/output/{}".format(pathInput)
    
    print("Type in the directory: ~/kharma/output/... :")
    pathInput = input()
    
    print("Type: image (1) or a movie (2)")
    type = int(input())
    
    if type == 1:
        print("Image number: ")
        imageNumber = int(input())
        print("Type frame: xy or xz")
        frame = input()
        print("Type variable ('rho', 'Pg', 'u^r', 'u^3', 'u_3', 'b', 'beta', 'inv_beta', 'Ptot', 'FM', 'FE') (log_..):")
        var = input()
        
        outDir = os.path.join(startingDirectory, "images")
        isOutDir = os.path.isdir(outDir)
        if isOutDir == False:
            os.mkdir(outDir)
        plotKharmaFrame(startingDirectory, imageNumber, frame, var)
    elif type == 2:
        print("Type frame: xy or xz")
        frame = input()
        print("Type variable ('rho', 'Pg', 'u^r', 'u^3', 'u_3', 'b', 'beta', 'inv_beta', 'Ptot', 'FM', 'FE') (log_..):")
        var = input()
        movieName = startingDirectory.split('/')[-1] + '_' + var + '.mp4'
        plotKharmaMovie(startingDirectory, movieName, frame, var)

        #FRAMES SHOULD BE DELETED IN BASH AFTER MOVIE CREATION!!
    '''
