#!/usr/bin/bash 

#---variables
SCRIPT_DIR="${SLURM_SUBMIT_DIR:-$(pwd)}"
BENCHPARK_HOME="$(cd "$SCRIPT_DIR/../../" && pwd)"
OUTPUT_DIR="./output"
BASE="ucx_perftest"
DEST1='GH200_base'
DEST2='GH200_test'
WS_BUILD="workspace_base"
WS_TEST="workspace_test"
BASE_NAME="CHECK_PARAM"
