#!/bin/bash
#SBATCH --job-name=slurm_vars
#SBATCH --output=vars_%A_%a.out
#SBATCH --error=vars_%A_%a.err
#SBATCH --nodes=2
#SBATCH --ntasks=8
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=2
#SBATCH --mem-per-cpu=2G
#SBATCH --gres=gpu:2
#SBATCH --time=01:00:00
#SBATCH --array=1-2
#SBATCH --partition=debug
#SBATCH --qos=normal
#SBATCH --reservation=maintenance
#SBATCH --account=research
#SBATCH --nice=100
#SBATCH --comment="Demonstrating Slurm variables"
#SBATCH --exclusive
#SBATCH --tmp=10G
#SBATCH --dependency=singleton
#SBATCH --begin=now+1hour
#SBATCH --deadline=now+2hours
#SBATCH --spread-job
#SBATCH --cpus-per-gpu=2
#SBATCH --threads-per-core=2
#SBATCH --nodelist=node[001-002]
#SBATCH --mail-type=ALL
#SBATCH --mail-user=user@example.com

echo "=== Job Information ==="
echo "Job ID (SLURM_JOB_ID): $SLURM_JOB_ID"
echo "Array Job ID (SLURM_ARRAY_JOB_ID): $SLURM_ARRAY_JOB_ID"
echo "Array Task ID (SLURM_ARRAY_TASK_ID): $SLURM_ARRAY_TASK_ID"
echo "Job Name (SLURM_JOB_NAME): $SLURM_JOB_NAME"
echo "Job QOS (SLURM_JOB_QOS): $SLURM_JOB_QOS"
echo "Partition (SLURM_JOB_PARTITION): $SLURM_JOB_PARTITION"
echo "Account (SLURM_JOB_ACCOUNT): $SLURM_JOB_ACCOUNT"
echo "Submit Directory (SLURM_SUBMIT_DIR): $SLURM_SUBMIT_DIR"
echo "Submit Host (SLURM_SUBMIT_HOST): $SLURM_SUBMIT_HOST"

echo -e "\n=== Resource Allocation ==="
echo "Number of Nodes (SLURM_JOB_NUM_NODES): $SLURM_JOB_NUM_NODES"
echo "Node List (SLURM_JOB_NODELIST): $SLURM_JOB_NODELIST"
echo "Node Name (SLURMD_NODENAME): $SLURMD_NODENAME"
echo "Tasks (SLURM_NTASKS): $SLURM_NTASKS"
echo "Tasks per Node (SLURM_TASKS_PER_NODE): $SLURM_TASKS_PER_NODE"
echo "CPUs per Task (SLURM_CPUS_PER_TASK): $SLURM_CPUS_PER_TASK"
echo "CPUs on Node (SLURM_CPUS_ON_NODE): $SLURM_CPUS_ON_NODE"
echo "Threads per Core (SLURM_THREADS_PER_CORE): $SLURM_THREADS_PER_CORE"
echo "Total Memory (SLURM_MEM_PER_NODE): $SLURM_MEM_PER_NODE"
echo "GPUs (SLURM_GPUS): $SLURM_GPUS"
echo "GPUs per Node (SLURM_GPUS_PER_NODE): $SLURM_GPUS_PER_NODE"
echo "GPUs per Task (SLURM_GPUS_PER_TASK): $SLURM_GPUS_PER_TASK"
echo "GPU Bind (SLURM_GPU_BIND): $SLURM_GPU_BIND"

echo -e "\n=== Topology Information ==="
echo "Topology (SLURM_TOPOLOGY_ADDR): $SLURM_TOPOLOGY_ADDR"
echo "Topology Addr Pattern (SLURM_TOPOLOGY_ADDR_PATTERN): $SLURM_TOPOLOGY_ADDR_PATTERN"

echo -e "\n=== Process Information ==="
echo "Local ID (SLURM_LOCALID): $SLURM_LOCALID"
echo "Process ID (SLURM_PROCID): $SLURM_PROCID"
echo "Node ID (SLURM_NODEID): $SLURM_NODEID"
echo "Task PID (SLURM_TASK_PID): $SLURM_TASK_PID"

echo -e "\n=== MPI Information ==="
echo "CPU Bind (SLURM_CPU_BIND): $SLURM_CPU_BIND"
echo "CPU Bind List (SLURM_CPU_BIND_LIST): $SLURM_CPU_BIND_LIST"
echo "CPU Bind Type (SLURM_CPU_BIND_TYPE): $SLURM_CPU_BIND_TYPE"

echo -e "\n=== Time Information ==="
echo "Job Start Time (SLURM_JOB_START_TIME): $SLURM_JOB_START_TIME"
echo "Job End Time (SLURM_JOB_END_TIME): $SLURM_JOB_END_TIME"
echo "Time Limit (SLURM_TIMELIMIT): $SLURM_TIMELIMIT"

echo -e "\n=== Working Directory Information ==="
echo "Current Working Directory: $(pwd)"
echo "Script Name: $0"
echo "Script Arguments: $@"

echo -e "\n=== Network Information ==="
echo "Network Interfaces: "
ip addr show

echo -e "\n=== Node Resource Usage ==="
echo "Memory Usage:"
free -h
echo -e "\nCPU Usage:"
mpstat 1 1
echo -e "\nGPU Usage:"
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi
else
    echo "nvidia-smi not available"
fi

echo -e "\n=== Environment Variables ==="
echo "All SLURM_* environment variables:"
env | grep ^SLURM_ | sort

echo -e "\n=== Job Step Information ==="
# Create a job step to demonstrate SLURM_STEP_* variables
srun --ntasks=2 bash -c 'echo "Job Step ID (SLURM_STEP_ID): $SLURM_STEP_ID"'

echo -e "\n=== Cluster Information ==="
scontrol show config
echo -e "\nPartition Information:"
scontrol show partition
echo -e "\nNode Information:"
scontrol show node $SLURM_JOB_NODELIST

# Example of using variables in a practical context
echo -e "\n=== Resource-Aware Task Distribution ==="
python3 << EOF
import os
import socket
import torch

def get_local_rank():
    return int(os.environ.get('SLURM_LOCALID', 0))

def get_world_size():
    return int(os.environ.get('SLURM_NTASKS', 1))

def get_rank():
    return int(os.environ.get('SLURM_PROCID', 0))

print(f"Node: {socket.gethostname()}")
print(f"Local Rank: {get_local_rank()}")
print(f"World Size: {get_world_size()}")
print(f"Global Rank: {get_rank()}")

if torch.cuda.is_available():
    gpu_id = get_local_rank() % torch.cuda.device_count()
    print(f"Assigned GPU: {gpu_id}")
EOF
