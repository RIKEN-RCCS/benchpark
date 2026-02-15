#!/bin/bash

if [ "$PARAM_LIST_DEFINED" != "true" ]; then
    echo "Error: This script cannot be run directly."
    echo "Must be run from a configuration script such as exec_exp.sh."
    echo "Please create the configuration script by referring to exec_exp_template.sh."
    exit 1
fi

#------------------------------------
# Controlling where it runs
#------------------------------------
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BENCHPARK_ROOT="$(cd "$SCRIPT_DIR/../../" && pwd)"
cd "$BENCHPARK_ROOT" || exit 1

#------------------------------------
# Checking for the existence of Parameter List
#------------------------------------
if [ ${#param_list[@]} -eq 0 ]; then
    echo "Error: param_list is not defined"
    exit 1
fi

#------------------------------------
# Import preferences 
#------------------------------------
if [ -f "setup-env.sh" ]; then
    . setup-env.sh
else
    echo "Error: setup-env.sh not found in $(pwd)"
    exit 1
fi
#[ -d ".venv" ] && source .venv/bin/activate
if [ ! -d ".venv_front" ]; then
    echo ".venv_front not found. Creating virtual environment and installing modules..."
    python3 -m venv .venv_front
    source .venv_front/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install .[analyze]
else
    source .venv_front/bin/activate
fi

#------------------------------------
# Path Settings and Create Directories
#------------------------------------
EXEC_ID=$(date +%Y%m%d_%H%M%S)
BASE_DIR="${BENCHPARK_ROOT}/workdir/nccl-tests"
RUN_ROOT="${BASE_DIR}/${EXEC_ID}"
SYSTEM_DIR="${BASE_DIR}/GH200_nvhpc"

mkdir -p "${BASE_DIR}" "${RUN_ROOT}"
MAP_FILE="${RUN_ROOT}/experiment_map.txt"
echo "Experiment ID: ${EXEC_ID}" > "$MAP_FILE"
echo "----------------------------------------" >> "$MAP_FILE"

#------------------------------------
# Serch Binary Path
#------------------------------------
SEARCH_ROOT="${BASE_DIR}/workspace/spack/opt/spack/linux-neoverse_v2/"
FOUND_PATHS=$(find ${SEARCH_ROOT} -name "nccl-tests-*" -type d -exec test -e "{}/bin" \; -print -quit)
COUNT=$(echo "$FOUND_PATHS" | grep -c /)
if [ "$COUNT" -eq 0 ]; then
    echo "Error: No nccl-tests binary directory found under $SEARCH_ROOT"
    exit 1
elif [ "$COUNT" -gt 1 ]; then
    echo "Error: Multiple nccl-tests directories found. Please clean up or specify one:"
    echo "$FOUND_PATHS"
    exit 1
fi
BIN_PATH="${FOUND_PATHS}/bin"
echo "Binary Path : $BIN_PATH"


# counter for experiment
EXP_COUNT=0

#------------------------------------
# Defining a recursive function
#------------------------------------
generate_combos() {
    local idx=$1      # Current parameter index
    local suffix=$2   # Suffix for directory names
    local args=$3     # parameter for benchpark

    # Once all parameters have been processed, execute the sequence of commands.
    if [ $idx -eq ${#param_list[@]} ]; then
        # Setting the experiment name and output destination
	EXP_COUNT=$((EXP_COUNT + 1))
	local exp_id=$(printf "exp_%05d" $EXP_COUNT)
	local ws_parent="${RUN_ROOT}/${exp_id}"

	printf "%-10s | %s\n" "$exp_id" "$args" >> "$MAP_FILE"
	
        # Run in a subshell (to prevent environment variables from becoming bloated)
        (
            echo "=========================================================="
	    echo "Processing [${exp_id}]: ${args}"
            echo "=========================================================="
            
            rm -rf "${SYSTEM_DIR}/nccl-tests"
            #rm -rf "${ws_parent}"

            # Benchpark Experiment Init
            benchpark experiment init "${SYSTEM_DIR}" nccl-tests+cuda \
                package_manager="user-managed" \
                prepend_path="${BIN_PATH}" \
                $args

            # Benchpark Setup
            benchpark setup "${SYSTEM_DIR}/nccl-tests" "${ws_parent}"

            # Loading the environment and running Ramble
            if [ -f "${ws_parent}/setup.sh" ]; then
                source "${ws_parent}/setup.sh"
                
                # ws_parent / SystemDirName / Benchmark Name / workspace
                local ramble_ws_dir="${ws_parent}/GH200_nvhpc/nccl-tests/workspace"
                
                echo "Ramble Workspace Setup: $ramble_ws_dir"
                ramble --workspace-dir "$ramble_ws_dir" workspace setup
                ramble --workspace-dir "$ramble_ws_dir" on
            fi
        )
        return
    fi

    # Get items from a parameter list
    local entry="${param_list[$idx]}"

    # Skip comment lines (#) and blank lines and go to the next
    if [[ -z "$entry" || "$entry" == "#"* ]]; then
        generate_combos $((idx + 1)) "$suffix" "$args"
        return
    fi

    # Decompose names, values, and comments
    local p_name p_values_str p_comment
    IFS=':' read -r p_name p_values_str p_comment <<< "$entry"
    local p_values
    IFS=',' read -r -a p_values <<< "$p_values_str"

    # Recursive call (loop) for each value
    for val in "${p_values[@]}"; do
        generate_combos $((idx + 1)) "${suffix}_${p_name}${val}" "$args ${p_name}=${val}"
    done
}

#------------------------------------
# Start execution
#------------------------------------
echo "Starting recursive experiment generation..."
generate_combos 0 "" ""

