#!/bin/bash
#SBATCH --time=2-0
#SBATCH --gpus=a100:1
#SBATCH --partition=uri-gpu
#SBATCH --cpus-per-task=16
#SBATCH --nodes=1
#SBATCH --mem=32g
#SBATCH --mail-type=ALL                                             # Type of email notification- BEGIN,END,FAIL,ALL
#SBATCH --mail-user=nikola.bukowiecka@uri.edu

HOST=$(hostname -f) source /work/pi_gkhanna_uri_edu/Nikola/kharma/machines/unity.sh
export LD_LIBRARY_PATH=/modules/opt/linux-ubuntu24.04-x86_64/nvhpc/Linux_x86_64/24.9/cuda/12.6/lib64:$LD_LIBRARY_PATH
srun --export=ALL,OMP_PROC_BIND=spread /work/pi_gkhanna_uri_edu/Nikola/kharma/kharma.cuda -i /work/pi_gkhanna_uri_edu/Nikola/kharma/pars/tori_3d/test_pars/mad_KerrLow.par

