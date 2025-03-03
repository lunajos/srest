#!/bin/bash
#SBATCH --job-name=job_chain
#SBATCH --output=chain_%j.out
#SBATCH --error=chain_%j.err
#SBATCH --time=01:00:00
#SBATCH --mem=4G

# This script demonstrates job chaining using srest
# It will create a chain of jobs with different dependencies

echo "Starting job chain orchestration..."

# Submit data preparation job
PREP_JOB=$(srest submit --parsable \
    --job-name=prep \
    --time=10:00 \
    --mem=2G \
    --wrap="echo 'Preparing data...'; sleep 30")

# Submit parallel processing jobs depending on prep
for i in {1..3}; do
    PROC_JOB[$i]=$(srest submit --parsable \
        --job-name=process_$i \
        --dependency=afterok:$PREP_JOB \
        --time=20:00 \
        --mem=4G \
        --wrap="echo 'Processing chunk $i'; sleep 60")
done

# Create dependency string for all processing jobs
DEP_STRING=$(IFS=:; echo "afterok:${PROC_JOB[*]}")

# Submit final aggregation job
FINAL_JOB=$(srest submit --parsable \
    --job-name=aggregate \
    --dependency=$DEP_STRING \
    --time=15:00 \
    --mem=8G \
    --wrap="echo 'Aggregating results...'; sleep 45")

# Monitor job chain status
srest job list --job $PREP_JOB ${PROC_JOB[@]} $FINAL_JOB
