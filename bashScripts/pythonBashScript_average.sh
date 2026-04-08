#!/bin/bash
#SBATCH --time=8:00:00
#SBATCH --ntasks=1 --cpus-per-task=6
#SBATCH -p uri-cpu,cpu
#SBATCH --nodes=1
#SBATCH --mem=8g
#SBATCH -c 6
#SBATCH --constraint=avx512

#SBATCH --mail-type=ALL                                             # Type of e>
#SBATCH --mail-user=nikola.bukowiecka@uri.edu
export OMP_NUM_THREADS=48
module load uri/main GSL/2.6-GCC-8.3.0
export LD_LIBRARY_PATH=$EBROOTGSL/lib:$LD_LIBRARY_PATH
module load conda/latest
conda activate bhi311

cd /project/u2grc/Nikola/vistools/

python3 average_hdf5_data.py /project/u2grc/Nikola/newSimulations/$1/ipole/n_-1_res_400