#!/usr/bin/bash

##### common variables #####
source ./common.sh

##### main loop #####
LIST_CUDA=( "" "cuda" )
LIST_GRAPH=( "" "graphing" )
LIST_MANAGED=( "" "managed" )
LIST_PAPI=( "" "papi" )

#--- build packages ---#
if [ ! -d ${OUTPUT_DIR}/${WS_BUILD} ]; then
    echo "##### build package #####"
    jid=$(sbatch --parsable build.sh)
    while squeue -j "$jid" >/dev/null 2>&1 && \
          [ "$(squeue -h -j "$jid")" != "" ]; do
        sleep 10
    done
fi

#--- setup experiments ---#
for p in "${LIST_PAPI[@]}"; do
    for m in "${LIST_MANAGED[@]}"; do
        for g in "${LIST_GRAPH[@]}"; do
            for c in "${LIST_CUDA[@]}"; do

                # Wait until there are fewer waiting jobs
                while true; do
                    job_count=$(squeue -u "$USER" -h | wc -l)
                    if [[ "$job_count" -lt 2  ]]; then
                        break
                    else
                        sleep 10
                    fi
                done
                echo "##### setup workload : ${c} ${g} ${m} ${p} #####"
                sbatch setup.sh  ${c} ${g} ${m} ${p}
            done
        done
    done
done

#--- execute experiments ---#
for p in "${LIST_PAPI[@]}"; do
    for m in "${LIST_MANAGED[@]}"; do
        for g in "${LIST_GRAPH[@]}"; do
            for c in "${LIST_CUDA[@]}"; do

                # Wait until there are fewer waiting jobs
                while true; do
                    job_count=$(squeue -u "$USER" -h | wc -l)
                    if [[ "$job_count" -lt 5  ]]; then
                        break
                    else
                        sleep 10
                    fi
                done
                sh ./experiment.sh  ${c} ${g} ${m} ${p}
            done
        done
    done
done


