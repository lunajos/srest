#!/bin/bash
#SBATCH --job-name=test
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=1:00
#SBATCH --chdir=/tmp/slurm_jobs/
#SBATCH --mcs-label=test_label
#SBATCH --mem=1G
#SBATCH --cpus-per-task=1
#SBATCH --output=test_%j.out
#SBATCH --error=test_%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=test@example.com

# Print node info to verify MCS label
scontrol show node $SLURM_NODELIST
sleep 60
