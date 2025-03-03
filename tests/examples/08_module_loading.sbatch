#!/bin/bash
#SBATCH --job-name=module_env
#SBATCH --output=modules_%j.out
#SBATCH --error=modules_%j.err
#SBATCH --time=00:30:00
#SBATCH --mem=8G

# Demonstrate sophisticated module loading and environment setup

# Function to check and load modules
load_module() {
    module=$1
    version=$2
    
    echo "Checking for $module/$version..."
    if module list 2>&1 | grep -q "$module/$version"; then
        echo "$module/$version already loaded"
    else
        echo "Loading $module/$version"
        module load $module/$version
    fi
}

# Clear existing modules
module purge

# Load required modules with version checking
load_module cuda 11.7
load_module gcc 9.3.0
load_module openmpi 4.1.4
load_module python 3.9

# Set environment variables
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export PYTHONPATH=/path/to/custom/packages:$PYTHONPATH

# Print environment information
echo "=== Environment Setup ==="
echo "Module List:"
module list
echo
echo "Environment Variables:"
env | sort
echo
echo "Python Information:"
python3 --version
pip list
echo
echo "GPU Information:"
nvidia-smi
echo
echo "MPI Information:"
mpirun --version
