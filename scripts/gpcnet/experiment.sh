#!/usr/bin/bash 

##### common variables #####
WORK_DIR=${PWD}
source ./common.sh

##### setting at benchpark home directory #####
cd ${BENCHPARK_HOME}
##### initialize python environment #####
if [ ! -d .venv_front ]; then
  . ./setup-env.sh
  python3.11 -m venv .venv_front
  source .venv_front/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
  pip install .[analyze]
fi
. ./setup-env.sh
source .venv_front/bin/activate

cd ${WORK_DIR}

##### run experiments at this directory #####
. ${OUTPUT_DIR}/${WORKSPACE}/setup.sh
ramble --workspace-dir ${OUTPUT_DIR}/${WORKSPACE}/${SYSTEM}/network_test/workspace on
ramble --workspace-dir ${OUTPUT_DIR}/${WORKSPACE}/${SYSTEM}/network_load_test/workspace on


