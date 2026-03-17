#!/bin/bash 
#SBATCH -n 1
#SBATCH -N 1
#SBATCH -p qc-gh200
#SBATCH --time 02:00:00

##### common variables #####
cd ${SLURM_SUBMIT_DIR}
source ./common.sh

##### module load #####
module load system/qc-gh200
module load nvhpc-hpcx-cuda12/25.7

##### setting at benchpark home directory #####
cd ${BENCHPARK_HOME}

##### initialize python environment #####
if [ ! -d .venv ]; then
  python3 -m venv .venv
  source .venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
  pip install .[analyze]
fi
. ./setup-env.sh
source .venv/bin/activate

##### build packages at this directory #####
cd ${SLURM_SUBMIT_DIR}
[ ! -d ${OUTPUT_DIR} ] && mkdir ${OUTPUT_DIR}

benchpark system init --dest=${OUTPUT_DIR}/${DEST1} qc-gh200 compiler=nvhpc_hpcx_cuda12
benchpark experiment init ${OUTPUT_DIR}/${DEST1} ${BASE}+cuda+xccl+papi+graphing+managed
benchpark setup ${OUTPUT_DIR}/${DEST1}/${BASE} ${OUTPUT_DIR}/${WS_BUILD}
. ${OUTPUT_DIR}/${WS_BUILD}/setup.sh
ramble --workspace-dir ${OUTPUT_DIR}/${WS_BUILD}/${DEST1}/${BASE}/workspace workspace setup

echo "--- build.sh has finished ---"

