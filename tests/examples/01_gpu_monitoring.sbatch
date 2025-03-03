#!/bin/bash
#SBATCH --job-name=gpu_monitor
#SBATCH --output=gpu_monitor_%j.out
#SBATCH --error=gpu_monitor_%j.err
#SBATCH --gres=gpu:1
#SBATCH --time=01:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G

# Load CUDA module
module load cuda/11.7

# Monitor GPU usage every 5 seconds
nvidia-smi dmon -s pucvt -i 0 -d 5 &
MONITOR_PID=$!

# Run deep learning training
python3 << EOF
import torch
import time

# Simple PyTorch computation to demonstrate GPU usage
device = torch.device('cuda')
x = torch.randn(1000, 1000).to(device)
y = torch.randn(1000, 1000).to(device)

for i in range(100):
    # Matrix multiplication
    z = torch.mm(x, y)
    time.sleep(1)  # Sleep to see GPU usage changes
EOF

# Stop monitoring
kill $MONITOR_PID
