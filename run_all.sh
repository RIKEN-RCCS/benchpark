#!/usr/bin/bash 

#---variables
BASE='osu-micro-benchmarks'

#---workload list : pick up from README in osu-micro-benchmarks-7.5.1
WORKLOAD_LIST_ALL=(  \
    "osu_alltoallw" "osu_allreduce" "osu_reduce" "osu_iallgather" \
    "osu_alltoall" "osu_scatterv" "osu_ialltoallw" "osu_iallreduce" \
    "osu_ineighbor_alltoall" "osu_gather" "osu_ineighbor_alltoallw" "osu_ialltoall" \
    "osu_neighbor_allgather" "osu_reduce_scatter" "osu_bcast" "osu_ineighbor_alltoallv" \
    "osu_ireduce" "osu_neighbor_alltoall" "osu_neighbor_allgatherv" "osu_neighbor_alltoallv" \
    "osu_ialltoallv" "osu_barrier" "osu_alltoallv" "osu_igather" \
    "osu_allgatherv" "osu_ineighbor_allgatherv" "osu_iscatter" "osu_igatherv" \
    "osu_gatherv" "osu_iscatterv" "osu_ireduce_scatter" "osu_ineighbor_allgather" \
    "osu_ibcast" "osu_neighbor_alltoallw" "osu_ibarrier" "osu_scatter" \
    "osu_allgather" "osu_iallgatherv" \
    "osu_put_bw" "osu_fop_latency" "osu_put_bibw" "osu_get_bw" "osu_cas_latency" \
    "osu_get_latency" "osu_put_latency" "osu_acc_latency" "osu_get_acc_latency" \
    "osu_latency_mp" "osu_bibw" "osu_latency" "osu_latency_mt" "osu_mbw_mr" \
    "osu_multi_lat" "osu_bw" \
    "osu_hello" "osu_init" \
    "osu_oshm_put_bw" "osu_oshm_get_nb" "osu_oshm_put_mr_nb" "osu_oshm_get_nb_bw" "osu_oshm_broadcast" \
    "osu_oshm_get_overlap" "osu_oshm_get_bw" "osu_oshm_put_nb_bw" "osu_oshm_get_mr_nb" "osu_oshm_put_overlap" \
    "osu_oshm_reduce" "osu_oshm_get" "osu_oshm_put" "osu_oshm_put_nb" "osu_oshm_collect" \
    "osu_oshm_atomics" "osu_oshm_barrier" "osu_oshm_put_mr" "osu_oshm_fcollect" \
    "osu_xccl_latency" "osu_xccl_bibw" "osu_xccl_bw" \
    "osu_xccl_reduce_scatter" "osu_xccl_alltoall" "osu_xccl_allgather" "osu_xccl_reduce" "osu_xccl_bcast" \
    "osu_xccl_allreduce" 
)
#WORKLOAD_LIST_ALL=( "osu_bibw" "osu_reduce" "osu_acc_latency" "osu_hello" "osu_oshm_collect" "osu_xccl_bw" "osu_xccl_reduce" )
WORKLOAD_LIST_OPTION_C=( "osu_bibw" "osu_bw" "osu_latency" "osu_mbw_mr" "osu_multi_lat" \
    "osu_put_latency" "osu_get_latency" "osu_put_bw" "osu_get_bw" "osu_put_bibw" \
    "osu_acc_latency" "osu_cas_latency" "osu_fop_latency" "osu_allgather" "osu_allgatherv" \
    "osu_allreduce" "osu_alltoall" "osu_alltoallv" "osu_bcast" "osu_gather" \
    "osu_gatherv" "osu_reduce" "osu_reduce_scatter" "osu_scatter" "osu_scatterv" \
    "osu_iallgather" "osu_iallgatherv" "osu_iallreduce" "osu_ialltoall" "osu_ialltoallv" \
    "osu_ialltoallw" "osu_ibcast" "osu_igather" "osu_igatherv" "osu_ireduce" \
    "osu_iscatter" "osu_iscatterv"
)
WORKLOAD_LIST_OPTION_G=( "osu_bibw" "osu_bw" "osu_latency" "osu_mbw_mr" "osu_multi_lat" \
    "osu_latency_mt" "osu_latency_mp" "osu_allgather" "osu_allgatherv" "osu_alltoall" \
    "osu_alltoallv" "osu_alltoallw" "osu_allreduce" "osu_bcast" "osu_gather" \
    "osu_gatherv" "osu_barrier" "osu_reduce" "osu_reduce_scatter" "osu_scatter" \
    "osu_scatterv" "osu_iallgather" "osu_iallgatherv" "osu_iallreduce" "osu_ialltoall" \
    "osu_ialltoallv" "osu_ialltoallw" "osu_ibarrier" "osu_ibcast" "osu_igather" \
    "osu_igatherv" "osu_ireduce" "osu_iscatter" "osu_iscatterv" "osu_put_latency" \
    "osu_get_latency" "osu_put_bw" "osu_get_bw" "osu_put_bibw" "osu_acc_latency" \
    "osu_cas_latency" "osu_fop_latency" "osu_get_acc_latency"
)
WORKLOAD_LIST_OPTION_M=( "osu_bibw" "osu_bw" "osu_latency" "osu_mbw_mr" "osu_multi_lat" \
    "osu_allgather" "osu_allgatherv" "osu_allreduce" "osu_alltoall" "osu_alltoallv" \
    "osu_bcast" "osu_gather" "osu_gatherv" "osu_reduce" "osu_reduce_scatter" \
    "osu_scatter" "osu_scatterv"
)
WORKLOAD_LIST_OPTION_P=( "osu_bibw" "osu_bw" "osu_latency" "osu_mbw_mr" "osu_multi_lat" \
    "osu_latency_mp" "osu_allgather" "osu_allgatherv" "osu_alltoall" "osu_alltoallv" \
    "osu_alltoallw" "osu_allreduce" "osu_bcast" "osu_gather" "osu_gatherv" \
    "osu_barrier" "osu_reduce" "osu_reduce_scatter" "osu_ireduce_scatter" "osu_scatter" \
    "osu_scatterv" "osu_iallgather" "osu_iallgatherv" "osu_iallreduce" "osu_ialltoall" \
    "osu_ialltoallv" "osu_ialltoallw" "osu_ibarrier" "osu_ibcast" "osu_igather" \
    "osu_igatherv" "osu_ireduce" "osu_iscatter" "osu_iscatterv" "osu_put_latency" \
    "osu_get_latency" "osu_put_bw" "osu_get_bw" "osu_put_bibw" "osu_acc_latency" \
    "osu_cas_latency" "osu_fop_latency" "osu_get_acc_latency"
)

initialize_python(){
    echo "##### initialize python environment #####"
    srun -N 1 -p qc-gh200 --time=00:10:00 bash << EOF1
    . ./setup-env.sh
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install .[analyze]
    exit
EOF1
}

build_packages(){
    echo "##### build packages #####"
    DEST1='GH200_nvhpc'
    WS_NAME1="workspace_base"
    srun -N 1 -p qc-gh200 --time=02:00:00 bash << EOF2
    module load system/qc-gh200
    module load nvhpc-hpcx-cuda12/25.7
    . setup-env.sh
    source .venv/bin/activate

    benchpark system init --dest=${DEST1} qc-gh200 compiler=nvhpc_hpcx
    benchpark experiment init ${DEST1} ${BASE}+cuda+xccl+papi+graphing+managed
    benchpark setup ${DEST1}/${BASE} ${WS_NAME1}
    . ./${WS_NAME1}/setup.sh
    ramble --workspace-dir ./${WS_NAME1}/${DEST1}/${BASE}/workspace workspace setup

    exit
EOF2
}

execute_workload(){
    DEST='GH200_nvhpc_test'
    WL_LIST="${1}"
    FEATURE="${2}"
    WS_BUILD="workspace_base"
    WS_NAME="workspace_test${FEATURE}"
    WS_NAME="${WS_NAME//+/_}"
    PREP_PATH="$(find ${PWD}/${WS_BUILD}/spack/opt/spack/linux-neoverse_v2/osu-micro-benchmarks-*/libexec/osu-micro-benchmarks/ -type d | tr '\n' ':' | sed 's/:$//')"
    echo "##### execute workload #####"
    echo "--- ${WL_LIST} ---"
    echo "--- ${FEATURE} ---"
    echo "--- ${WS_NAME} ---"

    srun -N 1 -p qc-gh200 --time=01:00:00 bash << EOF3
    module load system/qc-gh200
    module load nvhpc-hpcx-cuda12/25.7
    . setup-env.sh
    source .venv/bin/activate
    [ -d ${DEST} ] && rm -rf ${DEST}
    benchpark system init --dest=${DEST} qc-gh200 compiler=nvhpc_hpcx
    benchpark experiment init ${DEST} ${BASE} ${FEATURE} workload="${WL_LIST}" prepend_path=\"${PREP_PATH}\" package_manager="user-managed"
    benchpark setup ${DEST}/${BASE} ${WS_NAME}
    . ${WS_NAME}/setup.sh
    ramble --workspace-dir ./${WS_NAME}/${DEST}/${BASE}/workspace workspace setup
    exit
EOF3

    # temporary fix
    find ./${WS_NAME}/${DEST}/${BASE}/workspace -name "execute_experiment" | xargs sed -i -e '/^#SBATCH[[:space:]]\+--gpus\b/d' -e 's/[[:space:]]\+--gpus[[:space:]]\+[0-9]\+//g'

    . ${WS_NAME}/setup.sh
    ramble --workspace-dir ./${WS_NAME}/${DEST}/${BASE}/workspace on

}

#check item is included or not
check_item_list(){
    local target="$1"
    shift

    for item in "$@"; do
        [[ "$item" == "$target" ]] && return 0
    done

    return 1
}

#========== ========== ==========
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
cat << EOF
USAGE:
$0 {cuda} {managed} {graph} {papi}
   cuda : enable for CUDA
   managed : enable for CUDA Managed Memory
   graph : enable for graphing
   papi : enable for PAPI

  example:
   $0            : all disabled
   $0 cuda       : CUDA is enabled
   $0 graph papi : graph and PAPI are enabled
EOF
exit 1
fi

#---create workload list
FLAG_C=false
FLAG_G=false
FLAG_M=false
FLAG_P=false
LIST_FEATURE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        cuda)
		FLAG_C=true
		LIST_FEATURE="${LIST_FEATURE}+cuda"
		shift
		;;
        graph)
		FLAG_G=true
		LIST_FEATURE="${LIST_FEATURE}+graphing"
		shift
		;;
        managed)
		FLAG_M=true
		LIST_FEATURE="${LIST_FEATURE}+managed"
		shift
		;;
        papi)
		FLAG_P=true
		LIST_FEATURE="${LIST_FEATURE}+papi"
		shift
		;;
        *)
		shift
		;;
    esac
done

LIST_WL=""
for a in "${WORKLOAD_LIST_ALL[@]}"; do
    if { ${FLAG_C} && ! check_item_list "$a" "${WORKLOAD_LIST_OPTION_C[@]}"; } || \
       { ${FLAG_G} && ! check_item_list "$a" "${WORKLOAD_LIST_OPTION_G[@]}"; } || \
       { ${FLAG_M} && ! check_item_list "$a" "${WORKLOAD_LIST_OPTION_M[@]}"; } || \
       { ${FLAG_P} && ! check_item_list "$a" "${WORKLOAD_LIST_OPTION_P[@]}"; }; then
        dammy=1
    else
        LIST_WL+="$a,"
    fi
done
LIST_WL="${LIST_WL%,}"

#---initialization & package build
[ ! -d .venv ] && initialize_python
[ ! -d workspace_base ] && build_packages

#---main
execute_workload "${LIST_WL}" "${LIST_FEATURE}"


