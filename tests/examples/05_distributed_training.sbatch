#!/bin/bash
#SBATCH --job-name=dist_train
#SBATCH --output=dist_train_%j.out
#SBATCH --error=dist_train_%j.err
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=1
#SBATCH --gres=gpu:2
#SBATCH --cpus-per-task=6
#SBATCH --mem=32G
#SBATCH --time=04:00:00

# Load required modules
module load cuda/11.7
module load anaconda

# Set up distributed environment
export MASTER_ADDR=$(hostname)
export MASTER_PORT=29500
export WORLD_SIZE=$SLURM_NTASKS
export NCCL_DEBUG=INFO

# Run distributed training
srun python3 << EOF
import os
import torch
import torch.distributed as dist
import torch.multiprocessing as mp
from torch.nn.parallel import DistributedDataParallel

def setup(rank, world_size):
    os.environ['MASTER_ADDR'] = os.environ['MASTER_ADDR']
    os.environ['MASTER_PORT'] = os.environ['MASTER_PORT']
    dist.init_process_group("nccl", rank=rank, world_size=world_size)

def cleanup():
    dist.destroy_process_group()

def train(rank, world_size):
    setup(rank, world_size)
    
    # Create model and move it to GPU
    model = torch.nn.Linear(20, 1).to(rank)
    ddp_model = DistributedDataParallel(model, device_ids=[rank])
    
    # Simulate training
    for epoch in range(10):
        # Generate fake data
        inputs = torch.randn(100, 20).to(rank)
        labels = torch.randn(100, 1).to(rank)
        
        # Forward pass
        outputs = ddp_model(inputs)
        loss = torch.nn.functional.mse_loss(outputs, labels)
        
        # Backward pass
        loss.backward()
        
        if rank == 0:
            print(f"Epoch {epoch}, Loss: {loss.item():.4f}")
    
    cleanup()

if __name__ == "__main__":
    world_size = int(os.environ['WORLD_SIZE'])
    rank = int(os.environ['SLURM_PROCID'])
    train(rank, world_size)
EOF
