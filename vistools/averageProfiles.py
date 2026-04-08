import matplotlib.pyplot as plt
import numpy as np
import os
import pyharm
import glob
from pyharm.ana import analyses as ana
import pickle
import argparse

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

    
def timeAveragedRProfiles(allFiles, pickleTimeAveRadProf, pickleTimeFunc):

    dump = pyharm.load_dump(allFiles[0])
    outDictRProfiles = {}
    ana.r_profiles(dump, outDictRProfiles, vars=('rho', 'UU', 'beta', 'sigma'))
    outDictRProfiles['r1d'] = dump['r1d']
    
    outDictBasic = {}
    ana.basic(dump, outDictBasic, t_avg_start=0, t_avg_end=np.inf)
    
    for file in allFiles[1:]:
        #print(file)
        dump = pyharm.load_dump(file)
        #Create time averaged radial profiles (one matrix from all dumps per each var)
        outDictRProfilesLoop = {}
        ana.r_profiles(dump, outDictRProfiles, vars=('rho', 'UU' ,'beta', 'sigma'))
        for key in list(outDictRProfilesLoop.keys()):
            outDictRProfiles[key] = (outDictRProfiles[key] + outDictRProfilesLoop[key]) / 2
            
        #Create time functions (
        outDictBasicLoop = {}
        ana.basic(dump, outDictBasicLoop, t_avg_start=0, t_avg_end=np.inf)
        for key in list(outDictBasicLoop.keys()):
            outDictBasic[key] = np.append(outDictBasic[key], outDictBasicLoop[key])
     
    #plt.plot(dump['r1d'], outDictRProfiles['rt/rho_disk'])
    #plt.show()
    
    #plt.plot(dump['r1d'], outDictRProfiles['rt/UU_disk'])
    #plt.show()
    
    #plt.plot(dump['r1d'], outDictRProfiles['rt/beta_disk'])
    #plt.show()
    
    #plt.plot(dump['r1d'], outDictRProfiles['rt/sigma_disk'])
    #plt.show()
    

    #U/rho - total tfluid temperature
    #ion portion (ion specific) split up U between between ions and electrons. Ratio for ions and electrons thats the beta
    #U is one of the primitives
    
    #appendix H of EHT sagg A paper 8
    
    with open(pickleTimeAveRadProf, 'wb') as openFile:
        pickle.dump(outDictRProfiles, openFile)
        
    with open(pickleTimeFunc, 'wb') as openFile:
        pickle.dump(outDictBasic, openFile)
    
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Create time averaged radial profiles and time functions.')
    parser.add_argument('startingDirectory', type = str, help = 'Type in the directory exe: /project/..')
    
    args = parser.parse_args()
     
    #startingDirectory = "/Users/nikolabukowiecka/Desktop/Nikola/BHIcollab/extract
    
    if os.path.isdir(os.path.join(args.startingDirectory, "pickle")) == False:
        os.mkdir(os.path.join(args.startingDirectory, "pickle"))
        
    pickleTimeAveRadProf = args.startingDirectory + "/pickle/timeAveRadProf.pkl"
    #pickleTimeAveRadProf = args.startingDirectory.split('/')[-1] + "/pickle/_timeAveRadProf.pkl"
    pickleTimeFunc = args.startingDirectory + "/pickle/timeFunc.pkl"
    #pickleTimeFunc = args.startingDirectory.split('/')[-1] + "/pickle/_timeFunc.pkl"
    
    allFiles = assembleFiles(args.startingDirectory)
    timeAveragedRProfiles(allFiles, pickleTimeAveRadProf, pickleTimeFunc)
    
    
