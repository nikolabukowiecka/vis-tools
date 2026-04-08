#!/bin/bash
#SBATCH --time=1:00:00
#SBATCH -q long
#SBATCH --ntasks=1 --cpus-per-task=6
#SBATCH -p uri-cpu,cpu
#SBATCH --nodes=1
#SBATCH --mem=8g
#SBATCH -c 6
#SBATCH --constraint=avx512
#SBATCH --mail-type=ALL
#SBATCH --mail-user=nikola.bukowiecka@uri.edu #don't need to specify if the same as account

export OMP_NUM_THREADS=48
module load uri/main GSL/2.6-GCC-8.3.0
export LD_LIBRARY_PATH=$EBROOTGSL/lib:$LD_LIBRARY_PATH

cd /project/u2grc/Nikola/newSimulations/$1
# use nullglob in case there are no matching files
shopt -s nullglob
arr=(*.h5)
var=1
#echo $var
#line=$ sed -n -e "$var {" -e p -e q -e "}" /project/u2grc/Nikola/ipole/mfitting/KerrLowResLowA/Mfit_file.txt
#echo $line
#var=$((var+1))
#echo $var
#line=$ sed -n -e "$var {" -e p -e q -e "}" /project/u2grc/Nikola/ipole/mfitting/KerrLowResLowA/Mfit_file.txt
#echo $line
#for ((i=2866; i<${#arr[@]}; i++)); do
# for ((i=2138; i<2865; i++)); do
for ((i=2865; i<2866; i++)); do
    echo "${arr[$i]}"
    Mfit=$( sed -n -e "$var {" -e p -e q -e "}" /project/u2grc/Nikola/ipole/mfitting/$1/Mfit_file.txt)
    #echo $var
    var=$((var+1))
    echo $Mfit
    #do something to each element of array
    /work/pi_gkhanna_uri_edu/Nikola/ipoleKH/ipole -par /work/pi_gkhanna_uri_edu/Nikola/ipoleKH/model/iharm/example.par --M_unit=$Mfit --dump=/project/u2grc/Nikola/newSimulations/$1/"${arr[$i]}" --outfile=/project/u2grc/Nikola/newSimulations/$1/ipole/n_-1_res_400/image_"${arr[$i]}"
done

#1 $1 = KerrLowResLowA

#arr=torus.out0.03000.h5
#echo $arr
#cd /work/pi_gkhanna_uri_edu/Nikola/ipole && ./ipole -par ./model/iharm/example.par --dump=/project/u2grc/Nikola/KerrLowResLowA/torus.out0.03000.h5 --outfile=/project/u2grc/Nikola/KerrLowResLowA/ipole/image_torus.out0.03000.h5 ; cd -


#cd /work/pi_gkhanna_uri_edu/Nikola/ipole
#make
#cd /project/u2grc/Nikola/vistools
#module load uri/main GSL/2.6-GCC-8.3.0
#export LD_LIBRARY_PATH=$EBROOTGSL/lib:$LD_LIBRARY_PATH
#export OMP_NUM_THREADS=48
#/work/pi_gkhanna_uri_edu/Nikola/ipole/ipole -par /work/pi_gkhanna_uri_edu/Nikola/ipole/model/iharm/example.par --M_unit=5.601465443889649e+24 --dump=/project/u2grc/Nikola/KerrLowResLowA/torus.out0.03001.h5 --outfile=/project/u2grc/Nikola/KerrLowResLowA/TEST_1600/image_1600_torus.out0.03001.h5
#module load conda/latest
#conda activate bhi311
#python3 plot_unpol_StokesI_interpolate.py /project/u2grc/Nikola/KerrLowResLowA/TEST_1600