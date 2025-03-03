#!/bin/bash
#SBATCH --job-name=hetero_steps
#SBATCH --output=hetero_%j.out
#SBATCH --error=hetero_%j.err
#SBATCH --time=02:00:00
#SBATCH --mem=32G
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=2
#SBATCH --gres=gpu:2

# Demonstrate heterogeneous job steps with different resource requirements

echo "Starting heterogeneous job steps..."

# Step 1: CPU-only data preparation (using 1 node)
srun --nodes=1 --ntasks=1 --gres=none \
    python3 -c "
import time
print('Step 1: CPU-only data preparation')
time.sleep(30)
"

# Step 2: GPU-accelerated processing (using all GPUs)
srun --nodes=2 --ntasks=4 --gres=gpu:2 \
    python3 << EOF
import torch
import time

gpu_id = torch.cuda.current_device()
node_id = torch.distributed.get_rank() if torch.distributed.is_initialized() else 0

print(f'Step 2: GPU processing on device {gpu_id}, node {node_id}')
time.sleep(60)
EOF

# Step 3: Mixed CPU/GPU analysis (some tasks on GPU, others on CPU)
srun --nodes=2 --ntasks=4 --gres=gpu:1 \
    python3 << EOF
import os
import torch
import numpy as np
import time

task_id = int(os.environ.get('SLURM_PROCID', 0))
use_gpu = task_id % 2 == 0  # Even tasks use GPU, odd tasks use CPU

if use_gpu:
    device = torch.device('cuda')
    data = torch.randn(1000, 1000).to(device)
    print(f'Task {task_id}: Processing on GPU')
else:
    data = np.random.randn(1000, 1000)
    print(f'Task {task_id}: Processing on CPU')

time.sleep(45)
EOF

# Step 4: Final CPU-only aggregation
srun --nodes=1 --ntasks=1 --gres=none \
    python3 -c "
import time
print('Step 4: CPU-only result aggregation')
time.sleep(30)
"

echo "All heterogeneous steps completed"
