#!/bin/bash
#SBATCH --job-name=resource_scale
#SBATCH --output=scale_%j.out
#SBATCH --error=scale_%j.err
#SBATCH --time=02:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=4

# Monitor resource usage and dynamically adjust
python3 << EOF
import psutil
import time
import os
import subprocess

def get_slurm_job_id():
    return os.environ['SLURM_JOB_ID']

def request_more_resources(job_id, mem_increase):
    cmd = f"scontrol update JobId={job_id} MinMemoryNode={mem_increase}G"
    subprocess.run(cmd, shell=True)

def monitor_and_scale():
    job_id = get_slurm_job_id()
    process = psutil.Process()
    
    # Simulate increasing workload
    data = []
    for i in range(10):
        # Simulate memory-intensive work
        data.append([0] * (1000000 * (i + 1)))
        
        # Get current memory usage
        mem_usage = process.memory_info().rss / (1024 * 1024 * 1024)  # GB
        cpu_usage = psutil.cpu_percent(interval=1)
        
        print(f"Step {i}:")
        print(f"Memory usage: {mem_usage:.2f}GB")
        print(f"CPU usage: {cpu_usage}%")
        
        # If memory usage is high, request more
        if mem_usage > 12:  # 75% of allocated
            print("Requesting more memory...")
            request_more_resources(job_id, 32)
        
        time.sleep(10)

if __name__ == "__main__":
    monitor_and_scale()
EOF
