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
  . ./setup-env.sh
  python3 -m venv .venv
  source .venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
  pip install .[analyze]
fi
. ./setup-env.sh
source .venv/bin/activate

##### build packages and setup experiments at this directory #####
cd ${SLURM_SUBMIT_DIR}
[ ! -d ${OUTPUT_DIR} ] && mkdir ${OUTPUT_DIR}

benchpark system init --dest=${OUTPUT_DIR}/GH200 qc-gh200

# workload="network_test"
benchpark experiment init ${OUTPUT_DIR}/GH200 gpcnet workload="network_test" --dest=gpcnet_test
benchpark setup ${OUTPUT_DIR}/GH200/gpcnet_test  ${OUTPUT_DIR}/${WORKSPACE1}
. ${OUTPUT_DIR}/${WORKSPACE1}/setup.sh
ramble --workspace-dir ${OUTPUT_DIR}/${WORKSPACE1}/GH200/gpcnet_test/workspace workspace setup

# workload="network_load_test"
benchpark experiment init ${OUTPUT_DIR}/GH200 gpcnet workload="network_load_test" --dest=gpcnet_load_test
benchpark setup ${OUTPUT_DIR}/GH200/gpcnet_load_test  ${OUTPUT_DIR}/${WORKSPACE2}
. ${OUTPUT_DIR}/${WORKSPACE2}/setup.sh
ramble --workspace-dir ${OUTPUT_DIR}/${WORKSPACE2}/GH200/gpcnet_load_test/workspace workspace setup

echo "--- build.sh has finished ---"

