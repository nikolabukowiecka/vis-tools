#!/bin/bash
##SBATCH --time=1-0
#SBATCH --time=8:00:00
#SBATCH --cpus-per-task=16
#SBATCH --nodes=1
#SBATCH --mem=16g
#SBATCH --mail-type=ALL                                             # Type of e>
#SBATCH --mail-user=nikola.bukowiecka@uri.edu

module load conda/latest
conda activate bhi311

module load ffmpeg/7.0.2
cd /project/u2grc/Nikola/vistools/

#python3 /project/pi_dgobeille_uri_edu/Nikola/write_to_file.py /project/pi_dgobeille_uri_edu/Nikola/madStable 1
#for ((i=0; i<3001; i++)); do
#    python3 plot.py /project/u2grc/Nikola/newSimulations/$1 1 xz log_rho -num
#    done
python3 plot.py /project/u2grc/Nikola/newSimulations/$1 2 xz log_rho
