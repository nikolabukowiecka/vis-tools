import matplotlib.pyplot as plt
import numpy as np
import os
import pyharm
import glob
from pyharm.ana import analyses as ana
import pickle
import argparse
import pandas as pd
import math

def mfit(paramsDirectory, mfittingConstantsDirectory, simulationName):

    mfitTable = pd.read_csv(os.path.join(mfittingConstantsDirectory, "mfittingTables.txt"), sep=" ")
    #print(mfitTable)
    Munit_a = mfitTable["Munit_a"].values[0]
    Munit_b = mfitTable["Munit_b"].values[0]

    #data = pd.read_pickle(pickleDirectory)
    data = pd.read_csv(paramsDirectory)

    t = data['coord/t']

    Mfit = [0 for x in range((len(t)))]
    Mfitfile = open(os.path.join(mfittingConstantsDirectory, "Mfit_file.txt"), "w")
    for i in range(len(t)):
        Mfit[i] = math.exp(float(t[i]) * (10**-6) * Munit_b + Munit_a)
        Mfitfile.write(str(Mfit[i]))
        Mfitfile.write("\n")
    Mfitfile.close()
    #print(Mfit)
    '''
    figure5, axis5 = plt.subplots(2,1) 
    axis5[0].plot(data['coord/t'], data['t/Mdot']*Mfit)
    axis5[0].set_title("Mdot") 

    axis5[1].plot(data['coord/t'], data['t/Phi_b']*Mfit)
    axis5[1].set_title("Phi_b") 

    #figure5.legend(simulationName, simulationName, loc="lower right")
    figure5.savefig(mfittingConstantsDirectory, dpi=500)
    plt.close(figure5)
    '''
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('startingDirectory', type = str, help = 'Type in the directory exe: /project/..')
    
    args = parser.parse_args()

    simulationName =  args.startingDirectory.split('/')[-1]
    print(simulationName)
    lenSimulationNameAndDir = len(args.startingDirectory.split('/')[-1]) + len(args.startingDirectory.split('/')[-2]) + 2
    lenSimulationName = len(args.startingDirectory.split('/')[-1]) + 1
    mfittingConstantsDirectory = os.path.join(args.startingDirectory[:-lenSimulationNameAndDir], "mfitting_test", str(simulationName))
    #print(mfittingConstantsDirectory)
    #print(os.listdir(mfittingConstantsDirectory))

    #pickleDirectory = os.path.join(args.startingDirectory, "pickle/timeFunc.pkl")
    #paramsDirectory = os.path.join(args.startingDirectory[:-lenSimulationName], ("params/jetParams_"+str(simulationName)+".csv"))
    paramsDirectory = os.path.join("/project/u2grc/Nikola/newSimulations/params/","jetParams_KerrLow.csv")
    mfit(paramsDirectory, mfittingConstantsDirectory, simulationName)
