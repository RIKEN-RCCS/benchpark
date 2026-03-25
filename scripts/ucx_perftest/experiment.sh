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

##### experiment.sh #####
TEST_CASE="$@"
if [ $# -eq 0 ]; then
  TARGET="${BASE_NAME}"
else
  TARGET="${BASE_NAME}_$@"
  TARGET="${TARGET// /_}"
  TARGET="${TARGET//=/_}"
fi

. ${OUTPUT_DIR}/${WS_TEST}/setup.sh
ramble --workspace-dir ${OUTPUT_DIR}/${WS_TEST}/${DEST2}/${TARGET}/workspace on

echo "--- experiment.sh has finished ---"

