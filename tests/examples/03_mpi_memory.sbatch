#!/bin/bash
#SBATCH --job-name=mpi_mem
#SBATCH --output=mpi_mem_%j.out
#SBATCH --error=mpi_mem_%j.err
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=4
#SBATCH --mem=64G
#SBATCH --time=02:00:00

# Load MPI module
module load openmpi

# Set OpenMP threads
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

# Run with memory monitoring
mpirun -n $SLURM_NTASKS \
    /usr/bin/time -v python3 << EOF
from mpi4py import MPI
import numpy as np
import psutil
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Allocate large array
data = np.random.rand(1000000)  # 8MB per process

# Monitor memory
process = psutil.Process()
mem_info = process.memory_info()

print(f"Rank {rank}: Memory usage = {mem_info.rss / 1024/1024:.2f} MB")

# Simulate computation and communication
for i in range(10):
    # All-to-all communication
    all_data = comm.allgather(data)
    time.sleep(1)
    
    if rank == 0:
        print(f"Step {i}: Total data size = {len(all_data) * len(data) * 8 / 1024/1024:.2f} MB")
EOF
