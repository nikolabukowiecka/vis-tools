
import numpy as np
import os
import glob
import argparse
import pandas as pd
import pickle

def assemblePickle(startingDirectory, mergedPickle):
    pth = os.path.join(startingDirectory, "pickle")
    allFiles = glob.glob(os.path.join(pth,"*pkl"))
    #print(allFiles)
    outDict= {}
    for file in allFiles:
        data = pd.read_pickle(file)
        outDict.update(data)
    #print(outDict.keys())
    with open(mergedPickle, 'wb') as openFile:
        pickle.dump(outDict, openFile)

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Read pickles of time averaged radial profiles and time functions.')
    parser.add_argument('startingDirectory', type = str, help = 'Type in the directory exe: /project/..')
    
    args = parser.parse_args()
    
    mergedPickle = args.startingDirectory + "/mergedPickle.pkl"
    assemblePickle(args.startingDirectory, mergedPickle)
    