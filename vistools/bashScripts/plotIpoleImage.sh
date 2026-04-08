#!/bin/bash
#SBATCH --time=8:00:00
#SBATCH --ntasks=1 --cpus-per-task=16
#SBATCH --partition=cpu
#SBATCH --nodes=1
#SBATCH --mem=16g
#SBATCH -c 16
#SBATCH --constraint=avx512
##SBATCH --mail-type=ALL                                             # Type of e>
##SBATCH --mail-user=nikola.bukowiecka@uri.edu
##SBATCH -d afterany:35639850

export OMP_NUM_THREADS=48
module load uri/main GSL/2.6-GCC-8.3.0
export LD_LIBRARY_PATH=$EBROOTGSL/lib:$LD_LIBRARY_PATH
module load FFmpeg/4.4.2-GCCcore-11.3.0
module load conda/latest
conda activate bhi311


cd /project/u2grc/Nikola/vistools

#shopt -s nullglob
#arr=(*.h5)

#for ((i=0; i<${#arr[@]}; i++)); do
#    echo "${arr[$i]}"
#    
#    python3 /project/u2grc/Nikola/vistools/plot_unpol_StokesI_interpolate.py /project/u2grc/Nikola/$1/ipole/n_1_res_400
#    done

python3 plot_pol_StokesI.py /project/u2grc/Nikola/newSimulations/$1/ipole/n_0_res_400