#!/bin/bash

#SBATCH --job-name=test_all_directives
#SBATCH --account=research
#SBATCH --partition=gpu
#SBATCH --time=2-00:00:00
#SBATCH --nodes=2
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --array=1-10
#SBATCH --dependency=afterany:1001
#SBATCH --qos=high
##SBATCH --mcs-label=test
#SBATCH --mail-type=ALL
#SBATCH --mail-user=test@example.com
#SBATCH --constraint=gpu:a100
#SBATCH --nodelist=node[001-004]
#SBATCH --exclude=node[005-008]

# This is a test script to verify directive parsing
echo "Running task $SLURM_ARRAY_TASK_ID"
echo "Running on node $SLURM_NODELIST"
echo "Using $SLURM_CPUS_ON_NODE CPUs"

# Simulate some work
sleep 60
