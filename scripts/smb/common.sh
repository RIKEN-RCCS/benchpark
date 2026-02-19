#!/usr/bin/bash 

#---variables
SCRIPT_DIR="${SLURM_SUBMIT_DIR:-$(pwd)}"
BENCHPARK_HOME="$(cd "$SCRIPT_DIR/../../" && pwd)"
BASE="smb"
SYSTEM="GH200"
OUTPUT_DIR="./output"
WORKSPACE="workspace"

