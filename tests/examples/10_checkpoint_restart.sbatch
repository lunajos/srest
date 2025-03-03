#!/bin/bash
#SBATCH --job-name=checkpoint
#SBATCH --output=checkpoint_%j.out
#SBATCH --error=checkpoint_%j.err
#SBATCH --time=04:00:00
#SBATCH --mem=16G
#SBATCH --signal=B:USR1@60

# Handler for SIGUSR1 signal (60 seconds before timeout)
_resubmit_self() {
    echo "Job ${SLURM_JOB_ID} received SIGUSR1 at $(date)"
    echo "Preparing checkpoint and resubmission..."
    
    # Save current progress
    echo $PROGRESS > checkpoint_${SLURM_JOB_ID}.txt
    
    # Resubmit the job
    srest submit $0
    
    # Exit current job gracefully
    exit 0
}

# Set up signal trap
trap _resubmit_self USR1

# Initialize or restore progress
if [ -f checkpoint_${SLURM_JOB_ID}.txt ]; then
    PROGRESS=$(cat checkpoint_${SLURM_JOB_ID}.txt)
else
    PROGRESS=0
fi

# Main processing loop with checkpointing
python3 << EOF
import time
import os
import signal
import sys

def save_checkpoint(progress, data):
    print(f"Saving checkpoint at progress {progress}%...")
    with open(f"data_checkpoint_{os.environ['SLURM_JOB_ID']}.py", 'w') as f:
        f.write(f"progress = {progress}\n")
        f.write(f"data = {data}\n")

def load_checkpoint():
    checkpoint_file = f"data_checkpoint_{os.environ['SLURM_JOB_ID']}.py"
    if os.path.exists(checkpoint_file):
        print("Loading from checkpoint...")
        checkpoint_data = {}
        with open(checkpoint_file) as f:
            exec(f.read(), checkpoint_data)
        return checkpoint_data['progress'], checkpoint_data['data']
    return 0, []

# Initialize or restore state
progress, data = load_checkpoint()
print(f"Starting/Resuming from progress: {progress}%")

# Main processing loop
try:
    while progress < 100:
        # Simulate some work
        time.sleep(5)
        data.append(progress)
        progress += 1
        
        # Periodic checkpoint
        if progress % 10 == 0:
            save_checkpoint(progress, data)
            print(f"Progress: {progress}%")
    
    print("Processing completed successfully!")

except Exception as e:
    print(f"Error occurred: {e}")
    save_checkpoint(progress, data)
    sys.exit(1)
EOF
