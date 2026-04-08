#!/bin/bash
##SBATCH --time=1-0
##SBATCH -q long
#SBATCH --time=2-0
#SBATCH --partition=uri-cpu,cpu
#SBATCH --ntasks=1
#SBATCH -p uri-cpu,cpu
#SBATCH --mem=6g
#SBATCH --cpus-per-task=48

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
module load uri/main GSL/2.6-GCC-8.3.0
export LD_LIBRARY_PATH=$EBROOTGSL/lib:$LD_LIBRARY_PATH
module load conda/latest
conda activate bhi311

cd /project/u2grc/Nikola/vistools/QuickImageStats

#python3 quick_analysis_multiple.py /project/u2grc/Nikola/newSimulations/$1/ipole/n_-1_res_400
python3 quick_analysis_multiple.py /project/u2grc/Nikola/newSimulations/$1/ipole/replot_n_-1_res_400