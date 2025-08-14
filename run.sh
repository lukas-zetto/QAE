#!/bin/bash
# 
# name of the job for better recognizing it in the queue overview
#SBATCH --job-name=test_job
# 
# define how many nodes we need
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#
# we only need 1 cpu at a time
#SBATCH --ntasks=1
#
# expected duration of the job
#              hh:mm:ss
#SBATCH --time=8:00:00
# 
# partition the job will run on
#SBATCH --partition cpu
# 
# expected memory requirements
#SBATCH --mem=1000MB
#SBATCH --array=1-8
#

OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
python main_copy_parallel.py \
    4 \
    1 \
    --num_threads 8 \
    --slurm_id ${SLURM_ARRAY_TASK_ID} \
    --window_size 20 \
    --stride 5 \
    --num_iterations 500 \
    --tester window_size \
    --ansatz 1
# Done
exit 0