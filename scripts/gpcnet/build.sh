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
if [ ! -d .venv_calc ]; then
  . ./setup-env.sh
  python3.11 -m venv .venv_calc
  source .venv_calc/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
  pip install .[analyze]
fi
. ./setup-env.sh
source .venv_calc/bin/activate

##### build packages and setup experiments at this directory #####
cd ${SLURM_SUBMIT_DIR}
[ ! -d ${OUTPUT_DIR} ] && mkdir ${OUTPUT_DIR}

benchpark system init --dest=${OUTPUT_DIR}/${SYSTEM} qc-gh200

# workload="network_test"
WL="network_test"
benchpark experiment init ${OUTPUT_DIR}/${SYSTEM} ${BASE} workload="${WL}" --dest=${WL}
benchpark setup ${OUTPUT_DIR}/${SYSTEM}/${WL}  ${OUTPUT_DIR}/${WORKSPACE}
. ${OUTPUT_DIR}/${WORKSPACE}/setup.sh
ramble --workspace-dir ${OUTPUT_DIR}/${WORKSPACE}/${SYSTEM}/${WL}/workspace workspace setup

# workload="network_load_test"
WL="network_load_test"
benchpark experiment init ${OUTPUT_DIR}/${SYSTEM} ${BASE} workload="${WL}" --dest=${WL}
benchpark setup ${OUTPUT_DIR}/${SYSTEM}/${WL}  ${OUTPUT_DIR}/${WORKSPACE}
. ${OUTPUT_DIR}/${WORKSPACE}/setup.sh
ramble --workspace-dir ${OUTPUT_DIR}/${WORKSPACE}/${SYSTEM}/${WL}/workspace workspace setup

echo "--- build.sh has finished ---"

