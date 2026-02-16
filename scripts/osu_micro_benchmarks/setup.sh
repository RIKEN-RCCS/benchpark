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
. ./setup-env.sh
source .venv/bin/activate

##### setup experiments at this directory #####
cd ${SLURM_SUBMIT_DIR}
[ ! -d ${OUTPUT_DIR} ] && mkdir ${OUTPUT_DIR}

#---
create_workload_list "$@"

WS_NAME="${WS_NAME_TEST}${LIST_FEATURE}"
WS_NAME="${WS_NAME//+/_}"
PREP_PATH="$(find ${SLURM_SUBMIT_DIR}/${OUTPUT_DIR}/${WS_BUILD}/spack/opt/spack/linux-neoverse_v2/${BASE}-*/libexec/${BASE}/ -type d | tr '\n' ':' | sed 's/:$//')"
echo "##### setup workload #####"
echo "--- ${LIST_WL} ---"
echo "--- ${LIST_FEATURE} ---"
echo "--- ${WS_NAME} ---"

[ ! -d ${OUTPUT_DIR}/${DEST2} ] && benchpark system init --dest=${OUTPUT_DIR}/${DEST2} qc-gh200 compiler=nvhpc_hpcx

benchpark experiment init ${OUTPUT_DIR}/${DEST2} ${BASE} ${LIST_FEATURE} workload="${LIST_WL}" prepend_path=\"${PREP_PATH}\" package_manager="user-managed"
benchpark setup ${OUTPUT_DIR}/${DEST2}/${BASE} ${OUTPUT_DIR}/${WS_NAME}
. ${OUTPUT_DIR}/${WS_NAME}/setup.sh
ramble --workspace-dir ${OUTPUT_DIR}/${WS_NAME}/${DEST2}/${BASE}/workspace workspace setup

echo "--- setup.sh has finished ---"

