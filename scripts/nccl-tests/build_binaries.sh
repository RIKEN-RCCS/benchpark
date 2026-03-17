#!/bin/bash
#SBATCH -n 1
#SBATCH -N 1
#SBATCH -p qc-gh200

#------------------------------------
# Controlling where it runs
#------------------------------------
#SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
#SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -n "$SLURM_JOB_ID" ]; then
    SCRIPT_FULL_PATH=$(scontrol show job "$SLURM_JOB_ID" | awk -F= '/Command=/{print $2}')
    SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_FULL_PATH")" && pwd)"
else
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi
BENCHPARK_ROOT="$(cd "$SCRIPT_DIR/../../" && pwd)"
cd "$BENCHPARK_ROOT" || exit 1

#------------------------------------
# Import preferences 
#------------------------------------
if [ -f "setup-env.sh" ]; then
    . setup-env.sh
else
    echo "Error: setup-env.sh not found in $(pwd)"
    exit 1
fi
if [ ! -d ".venv_calc" ]; then
    echo ".venv_calc not found. Creating virtual environment and installing modules..."
    python3 -m venv .venv_calc
    source .venv_calc/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install .[analyze]
else
    source .venv_calc/bin/activate
fi

#------------------------------------
# build all of execute binaries
#------------------------------------
mkdir -p ./workdir/nccl-tests
SYSTEM_DIR=./workdir/nccl-tests/GH200_nvhpc
WORKSPACE=./workdir/nccl-tests/workspace
benchpark system init --dest=${SYSTEM_DIR} qc-gh200 compiler=nvhpc_hpcx_cuda12
benchpark experiment init ${SYSTEM_DIR} nccl-tests+cuda
benchpark setup ${SYSTEM_DIR}/nccl-tests ${WORKSPACE}
. ${WORKSPACE}/setup.sh
ramble --workspace-dir ${WORKSPACE}/GH200_nvhpc/nccl-tests/workspace workspace setup

