#!/bin/bash
#SBATCH --time=8:00:00
#SBATCH --ntasks=1 --cpus-per-task=16
#SBATCH --partition=cpu
#SBATCH --nodes=1
#SBATCH --mem=16g
#SBATCH -c 16

export OMP_NUM_THREADS=48
module load conda/latest
conda activate bhi311

cd /project/u2grc/Nikola/vistools/QuickImageStats

python3 quick_analysis_multiple.py $1