#!/bin/bash
#SBATCH --job-name=notify_job
#SBATCH --output=notify_%j.out
#SBATCH --error=notify_%j.err
#SBATCH --mail-type=BEGIN,END,FAIL,TIME_LIMIT_90
#SBATCH --mail-user=user@example.com
#SBATCH --time=01:00:00
#SBATCH --mem=8G

# Function to simulate progress
report_progress() {
    echo "[$(date)] Progress: $1%"
    if [ "$2" = "error" ]; then
        return 1
    fi
}

# Simulate long-running job with progress updates
for i in {1..100}; do
    # Simulate random failures
    if [ $((RANDOM % 20)) -eq 0 ]; then
        report_progress $i "error"
        echo "Job failed at ${i}% progress"
        exit 1
    fi
    
    report_progress $i
    sleep 30
done

# Success message
echo "Job completed successfully!"
