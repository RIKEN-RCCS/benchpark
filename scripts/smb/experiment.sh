#!/bin/bash

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
ramble --workspace-dir ${OUTPUT_DIR}/${WORKSPACE}/${SYSTEM}/mpi_overhead/workspace on
ramble --workspace-dir ${OUTPUT_DIR}/${WORKSPACE}/${SYSTEM}/msgrate/workspace on

##### run experiments at this directory #####
OUTPUT_DIR="${OUTPUT_DIR}_mt"
. ${OUTPUT_DIR}/${WORKSPACE}/setup.sh
ramble --workspace-dir ${OUTPUT_DIR}/${WORKSPACE}/${SYSTEM}/rma_mt_mpi/workspace on


