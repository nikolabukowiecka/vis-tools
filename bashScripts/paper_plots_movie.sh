#!/bin/bash
#SBATCH --time=08:00:00
#SBATCH --partition=uri-cpu,cpu
#SBATCH --cpus-per-task=16
#SBATCH --mem=6G
#SBATCH --constraint=avx512

module load uri/main GSL/2.6-GCC-8.3.0
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export LD_LIBRARY_PATH=$EBROOTGSL/lib:$LD_LIBRARY_PATH
module load ffmpeg/7.0.2

module load conda/latest
conda activate bhi311

cd /project/u2grc/Nikola/vistools

python3 paper_plots_movie.py $1 $SLURM_CPUS_PER_TASK