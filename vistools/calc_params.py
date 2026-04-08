import matplotlib.pyplot as plt
import numpy as np
import os
import pyharm
import glob
from pyharm.ana import analyses as ana
import pickle
import argparse
import pandas as pd

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

    
def calc_params(allFiles, name):
    dump = pyharm.load_dump(allFiles[0])
    #outDictRadialProfiles = {}
    #ana.r_profiles(dump, outDictRadialProfiles, vars=('m', 'UU', 'beta', 'sigma'))
    #outDictRadialProfiles['r1d'] = dump['r1d']
    out = {}
    ana.basic(dump, out, t_avg_start=0, t_avg_end=np.inf)
    #outDictBasic = {'coord/t': out['coord/t'], 't/Mdot_5': out['t/Mdot_5'], 't/Edot_5': out['t/Edot_5'], 't/Phi_b': out['t/Phi_b'],}
    outDictBasic = {'coord/t': out['coord/t'], 't/Mdot_5': out['t/Mdot_5'], 't/Edot_5': out['t/Edot_5'], 
                    't/Mdot_10': out['t/Mdot_10'], 't/Edot_10': out['t/Edot_10'],
                    't/Mdot_50': out['t/Mdot_50'], 't/Edot_50': out['t/Edot_50'], 't/Phi_b': out['t/Phi_b'],}
    #print(outDictBasic) 

    for file in allFiles[1:]:
        #print(file)
        dump = pyharm.load_dump(file)
        outDictBasicLoop = {}
        ana.basic(dump, outDictBasicLoop, t_avg_start=0, t_avg_end=np.inf)
        outDictBasic['coord/t'] = np.append(outDictBasic['coord/t'], outDictBasicLoop['coord/t'])
        outDictBasic['t/Mdot_5'] = np.append(outDictBasic['t/Mdot_5'], outDictBasicLoop['t/Mdot_5'])
        outDictBasic['t/Edot_5'] = np.append(outDictBasic['t/Edot_5'], outDictBasicLoop['t/Edot_5'])
        outDictBasic['t/Mdot_10'] = np.append(outDictBasic['t/Mdot_10'], outDictBasicLoop['t/Mdot_10'])
        outDictBasic['t/Edot_10'] = np.append(outDictBasic['t/Edot_10'], outDictBasicLoop['t/Edot_10'])
        outDictBasic['t/Mdot_50'] = np.append(outDictBasic['t/Mdot_50'], outDictBasicLoop['t/Mdot_50'])
        outDictBasic['t/Edot_50'] = np.append(outDictBasic['t/Edot_50'], outDictBasicLoop['t/Edot_50'])
        outDictBasic['t/Phi_b'] = np.append(outDictBasic['t/Phi_b'], outDictBasicLoop['t/Phi_b'])
    
    outDictBasic['coord/t'] = outDictBasic['coord/t'].flatten()
    outDictBasic['t/Mdot_5'] = outDictBasic['t/Mdot_5'].flatten()
    outDictBasic['t/Edot_5'] = outDictBasic['t/Edot_5'].flatten()
    outDictBasic['t/Mdot_10'] = outDictBasic['t/Mdot_10'].flatten()
    outDictBasic['t/Edot_10'] = outDictBasic['t/Edot_10'].flatten()
    outDictBasic['t/Mdot_50'] = outDictBasic['t/Mdot_50'].flatten()
    outDictBasic['t/Edot_50'] = outDictBasic['t/Edot_50'].flatten()
    outDictBasic['t/Phi_b'] = outDictBasic['t/Phi_b'].flatten()

    df = pd.DataFrame(outDictBasic)
    df.to_csv('jetParams_'+str(name)+'.csv', index=False)
    
    
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Calc jet params.')
    parser.add_argument('startingDirectory', type = str, help = 'Type in the directory exe: /project/..')
    
    args = parser.parse_args()

    allFiles = assembleFiles(args.startingDirectory)
    name = args.startingDirectory.split('/')[5]
    calc_params(allFiles, name)
    
    

