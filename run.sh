#!/bin/bash
# 
# name of the job for better recognizing it in the queue overview
#SBATCH --job-name=test_job
# 
# define how many nodes we need
#SBATCH --nodes=1
#
# we only need 1 cpu at a time
#SBATCH --ntasks=1
#
# expected duration of the job
#              hh:mm:ss
#SBATCH --time=4:00:00
# 
# partition the job will run on
#SBATCH --partition single
# 
# expected memory requirements
#SBATCH --mem=64000MB

python main_copy.py 4 1 --num_threads 8

# Done
exit 0