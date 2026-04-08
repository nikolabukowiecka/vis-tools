#!/bin/bash
#SBATCH --time=8:00:00
#SBATCH --nodes=1
#SBATCH --mem=16g
#SBATCH -c 16
#SBATCH --mail-type=ALL                                             # Type of e>
#SBATCH --mail-user=nikola.bukowiecka@uri.edu

module load conda/latest
conda activate bhi311

module load ffmpeg/7.0.2

cd /project/u2grc/Nikola/vistools/
python3 plot_pol.py /project/u2grc/Nikola/newSimulations/$1/ipole/n_1_res_400
