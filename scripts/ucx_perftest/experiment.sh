#!/usr/bin/bash 

##### common variables #####
source ./common.sh

#---

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

