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
PREP_PATH="$(find ${SLURM_SUBMIT_DIR}/${OUTPUT_DIR}/${WS_BUILD}/spack/opt/spack/linux-neoverse_v2/${BASE}-*/ -type d -name "bin" | tr '\n' ':' | sed 's/:$//')"
TEST_CASE="$@"
if [ $# -eq 0 ]; then
  TARGET="${BASE_NAME}"
else
  TARGET="${BASE_NAME}_$@"
  TARGET="${TARGET// /_}"
  TARGET="${TARGET//=/_}"
fi

[ ! -d ${OUTPUT_DIR}/${DEST2} ] && benchpark system init --dest=${OUTPUT_DIR}/${DEST2} qc-gh200 compiler=nvhpc_hpcx

benchpark experiment init ${OUTPUT_DIR}/${DEST2} ${BASE} +cuda+verbs+rc+ud+dc+ib_hw_tm+rdmacm+mlx5 prepend_path=${PREP_PATH} package_manager="user-managed" ${TEST_CASE} --dest=${TARGET}

benchpark setup ${OUTPUT_DIR}/${DEST2}/${TARGET}  ${OUTPUT_DIR}/${WS_TEST}
. ${OUTPUT_DIR}/${WS_TEST}/setup.sh
ramble --workspace-dir ${OUTPUT_DIR}/${WS_TEST}/${DEST2}/${TARGET}/workspace  workspace setup

echo "--- setup.sh has finished ---"

