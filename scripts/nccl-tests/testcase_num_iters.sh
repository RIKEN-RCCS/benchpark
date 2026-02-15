#!/bin/bash

#------------------------------------
# Parameter List
#    If you comment out (#), the parameter will not be included in the loop 
#    and the default value will be used.
#    Format is  <param_name>:<value1>[,<value2>,...]:<comment>
#------------------------------------
param_list=(
    #"workload:all-to-all,all-reduce,all-gather,reduce-scatter,send-recv,broadcast,gather,reduce,scatter,hypercube:default all-reduce"
    #"nprocs:2,4:MPI processes default 2"
# +++ Number of GPUs +++
    #"nthreads_proc:1,2,4:-t <num threads> default 1"
    #"ngpus_thread:1,2,4:-g <GPUs per thread> default 1"
# +++ Sizes to scan(-i and -e) +++
    "min_bytes:16M:-b <min size in bytes> default 32M"
    #"min_bytes:8M,16M,32M:-b <min size in bytes> default 32M"
    #"max_bytes:32M,64M,128M:-e <max size in bytes> default 32M"
    #"step_inc:1M,2M,4M:-i <increment size> default 1M"
    #"step_factor:2,4:-f <increment factor> default disabled"
# +++ NCCL operations arguments +++
    #"op:sum,prod,min,max,avg,all:-o <sum/prod/min/max/avg/all> default sum"
    #"datatype:int8,uint8,int32,uint32,int64,uint64,half,float,double,bfloat16,f8e4m3,f8e5m2,all:-d <nccltype/all> default Float"
    #"root:0,1:-r <root/all> default 0"
# +++Performance +++
    "num_iters:20,40,60,80,100:-n <iteration count> default 20"
    #"warmup_iters:1,10:-w <warmup iteration count> default 1"
    #"agg_iters:5,10,20:-m <aggregation count> default 1"
    #"run_cycles:1,5,10:-N <cycle count> default 1"
    #"average:0,1,2,3:-a <0/1/2/3> default 1"
# +++ Test operation +++
    #"parallel_init:0,1:-p <0/1> default 0"
    #"result_check:1,2:-c <check iteration count> default 1"
    #"blocking:0,1:-z <0/1> default 0"
    #"cudagraph:0,5,10:-G <num graph launches> default 0"
    #"report_cputime:0,1:-C <0/1> default 0"
    #"local_register:0,1,2:-R <0/1/2> default 0"
    #"report_timestamps:0,1:-S <0/1> default 0"
    #"output_file:output.json:-J <file>"
    #"timeout:0,1,100:-T <time in seconds> default disabled"
)

#------------------------------------
# Call experiment_core.sh
#------------------------------------
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
export PARAM_LIST_DEFINED=true
source ${SCRIPT_DIR}/experiment_core.sh

