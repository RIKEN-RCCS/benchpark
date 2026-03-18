#!/bin/bash

#------------------------------------
# Controlling where it runs
#------------------------------------
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

${SCRIPT_DIR}/testcase_agg_iters.sh
${SCRIPT_DIR}/testcase_average.sh
${SCRIPT_DIR}/testcase_blocking.sh
${SCRIPT_DIR}/testcase_cudagraph.sh
${SCRIPT_DIR}/testcase_datatype.sh
${SCRIPT_DIR}/testcase_local_register.sh
${SCRIPT_DIR}/testcase_max_bytes.sh
${SCRIPT_DIR}/testcase_min_bytes.sh
${SCRIPT_DIR}/testcase_ngpu_thread.sh
${SCRIPT_DIR}/testcase_nprocs.sh
${SCRIPT_DIR}/testcase_nthreads.sh
${SCRIPT_DIR}/testcase_num_iters.sh
${SCRIPT_DIR}/testcase_op.sh
${SCRIPT_DIR}/testcase_output_file.sh
${SCRIPT_DIR}/testcase_paralell_init.sh
${SCRIPT_DIR}/testcase_report_cputime.sh
${SCRIPT_DIR}/testcase_report_timestanmps.sh
${SCRIPT_DIR}/testcase_result_check.sh
${SCRIPT_DIR}/testcase_root.sh
${SCRIPT_DIR}/testcase_run_cycles.sh
${SCRIPT_DIR}/testcase_step_factor.sh
${SCRIPT_DIR}/testcase_step_inc.sh
${SCRIPT_DIR}/testcase_timeout.sh
${SCRIPT_DIR}/testcase_warmup_iters.sh
${SCRIPT_DIR}/testcase_workload.sh

