#!/bin/bash
#SBATCH --time=1-0
#SBATCH --nodes=1
#SBATCH --mem=16g
#SBATCH -c 16
#SBATCH --mail-type=ALL                                             # Type of e>
#SBATCH --mail-user=nikola.bukowiecka@uri.edu

module load conda/latest
conda activate bhi311

cd /project/u2grc/Nikola/vistools/

python3 calc_params.py /project/u2grc/Nikola/newSimulations/$1

#run: sbatch pythonBashScrip_calcJetEff.sh KerrLow