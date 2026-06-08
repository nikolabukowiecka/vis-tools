#!/bin/bash
#SBATCH --time=1-0
#SBATCH --cpus-per-task=32
#SBATCH --nodes=1
#SBATCH --mem=16g

module load conda/latest
conda activate bhi311

#covert all .phdf files in a directory:
./pyharm-convert /project/u2grc/Nikola/newSimulations/$1/*.phdf --nthreads $SLURM_CPUS_PER_TASK



#convert a range of files in a directory: THIS WAY DOESN'T USE MULTITHREADING, because it does file by file
#cd /project/u2grc/Nikola/newSimulations/$1
#shopt -s nullglob
#arr=(*.phdf)
#var=1
#for ((i=3000; i<6001; i++)); do
#    echo "${arr[$i]}"
#    /work/pi_gkhanna_uri_edu/Nikola/pyharm/scripts/pyharm-convert ./"${arr[$i]}"
#done