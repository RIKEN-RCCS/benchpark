#!/usr/bin/bash 

##### common variables #####
WORK_DIR=${PWD}
source ./common.sh

##### setting at benchpark home directory #####
cd ${BENCHPARK_HOME}
. ./setup-env.sh
source .venv/bin/activate
cd ${WORK_DIR}

##### run experiments at this directory #####
. ${OUTPUT_DIR}/${WORKSPACE1}/setup.sh
ramble --workspace-dir ${OUTPUT_DIR}/${WORKSPACE1}/GH200/gpcnet_test/workspace on

. ${OUTPUT_DIR}/${WORKSPACE2}/setup.sh
ramble --workspace-dir ${OUTPUT_DIR}/${WORKSPACE2}/GH200/gpcnet_load_test/workspace on


