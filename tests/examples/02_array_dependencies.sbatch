#!/bin/bash
#SBATCH --job-name=array_dep
#SBATCH --output=array_%A_%a.out
#SBATCH --error=array_%A_%a.err
#SBATCH --array=1-4%2  # Run 4 tasks, max 2 concurrent
#SBATCH --time=00:30:00
##SBATCH --mem=1

echo "Processing chunk $SLURM_ARRAY_TASK_ID"

# Simulate different processing times
sleep $((RANDOM % 30))

# Create output for next stage
echo "Data from task $SLURM_ARRAY_TASK_ID" > chunk_$SLURM_ARRAY_TASK_ID.txt

# Submit dependent job only when array completes
if [ "$SLURM_ARRAY_TASK_ID" == "4" ]; then
    # Using srest to submit dependent job
    srest submit --dependency=afterok:$SLURM_ARRAY_JOB_ID merge_results.sbatch
fi
