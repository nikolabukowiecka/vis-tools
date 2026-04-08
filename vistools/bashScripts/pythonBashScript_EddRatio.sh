#!/bin/bash
#SBATCH --time=1-0
#SBATCH -q long
#SBATCH --ntasks=1 --cpus-per-task=6
#SBATCH -p uri-cpu,cpu
#SBATCH --nodes=1
#SBATCH --mem=6g
#SBATCH -c 6


export OMP_NUM_THREADS=48
module load uri/main GSL/2.6-GCC-8.3.0
export LD_LIBRARY_PATH=$EBROOTGSL/lib:$LD_LIBRARY_PATH
module load conda/latest
conda activate bhi311

cd /project/u2grc/Nikola/vistools

python3 calc_Edd_ratio.py /project/u2grc/Nikola/newSimulations/$1/ipole/n_-1_res_400