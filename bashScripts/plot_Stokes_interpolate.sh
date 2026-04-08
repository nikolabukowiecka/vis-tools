#!/bin/bash
#SBATCH --time=1-0
#SBATCH -p uri-cpu,cpu
#SBATCH --nodes=1
#SBATCH --mem=6g
#SBATCH --cpus-per-task=48
#SBATCH --constraint=avx512

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
module load conda/latest
conda activate bhi311

cd /project/u2grc/Nikola/vistools

python3 plot_pol_StokesI_interpolate.py /project/u2grc/Nikola/newSimulations/$1/ipole/replot_n_-1_res_400