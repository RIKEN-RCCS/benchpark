#!/usr/bin/bash 

##### common variables #####
source ./common.sh

#---
create_workload_list "$@"

WS_NAME="${WS_NAME_TEST}${LIST_FEATURE}"
WS_NAME="${WS_NAME//+/_}"
DEST3="test${LIST_FEATURE}"
DEST3="${DEST3//+/_}"
echo "##### execute workload #####"
echo "--- ${LIST_WL} ---"
echo "--- ${LIST_FEATURE} ---"
echo "--- ${WS_NAME} ---"

# temporary fix
find ${OUTPUT_DIR}/${WS_NAME}/${DEST2}/${BASE}/workspace -name "execute_experiment" | xargs sed -i -e '/^#SBATCH[[:space:]]\+--gpus\b/d' -e 's/[[:space:]]\+--gpus[[:space:]]\+[0-9]\+//g'

. ${OUTPUT_DIR}/${WS_NAME}/setup.sh
ramble --workspace-dir ${OUTPUT_DIR}/${WS_NAME}/${DEST2}/${DEST3}/workspace on


echo "--- ${LIST_WL} ---"
echo "--- ${LIST_FEATURE} ---"
echo "--- ${WS_NAME} ---"
echo "--- experiment.sh has finished ---"

