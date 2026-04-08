#!/bin/bash
#SBATCH --time=2-0
#SBATCH -p uri-cpu
#SBATCH --cpus-per-task=32
##SBATCH --nodes=1
#SBATCH --mem=16g
## SBATCH --mail-type=ALL
## SBATCH --mail-user=nikola.bukowiecka@uri.edu
#SBATCH --constraint=avx512

module load hdf5/1.14.5
module load uri/main GSL/2.6-GCC-8.3.0
export LD_LIBRARY_PATH=$EBROOTGSL/lib:$LD_LIBRARY_PATH
#export OMP_NUM_THREADS=32
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

module load conda/latest
conda activate bhi311

python3 -u fit_loglinear_munit.py 0
