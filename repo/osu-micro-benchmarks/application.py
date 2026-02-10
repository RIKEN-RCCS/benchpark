# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import sys

from ramble.app.builtin.osu_micro_benchmarks import (
    OsuMicroBenchmarks as OsuMicroBenchmarksBase,
)
from ramble.appkit import *


class OsuMicroBenchmarks(OsuMicroBenchmarksBase):

    tags = ['synthetic',
            'large-scale','multi-node','single-node',
            'atomics','managed-memory',
            'mpi','openshmem','upc','upc++','nccl','rccl',
            'network-bandwidth-bound','network-bisection-bandwidth-bound',
            'network-collectives','network-latency-bound',
            'network-multi-threaded','network-nonblocking-collectives',
            'network-onesided','network-point-to-point',
            'c','java','python','openacc']

    # 実行テンプレート
    executable('run_mpi', '{pre_run_cmds}\n{mpi_command} {benchmark_name} {additional_args}', use_mpi=True)
    executable('run_mpi4', '{pre_run_cmds}\n{mpi_command} -n 4 {benchmark_name} {additional_args}', use_mpi=True)
    executable('run_mpi_MT', '{pre_run_cmds}\n{export_environments} {mpi_command} {benchmark_name} {additional_args}', use_mpi=True)

    # workloads
    wl_mpi_pt2pt = ['osu_bibw', 'osu_bw', 'osu_latency', 'osu_latency_mp', 'osu_latency_mt',
                    'osu_mbw_mr', 'osu_multi_lat'
    ]
    for exe in wl_mpi_pt2pt:
        if exe == 'osu_latency_mt':
            workload(exe, executables=['run_mpi_MT'])
        else:
            workload(exe, executables=['run_mpi'])

    wl_mpi_pt2pt_p = ['osu_bibw_persistent', 'osu_bw_persistent', 'osu_latency_persistent']
    for exe in wl_mpi_pt2pt_p:
        workload(exe, executables=['run_mpi'])

    wl_mpi_collective = ['osu_alltoallw', 'osu_allreduce', 'osu_reduce', 'osu_iallgather', 'osu_alltoall',
                         'osu_scatterv', 'osu_ialltoallw', 'osu_iallreduce', 'osu_gather', 'osu_ialltoall',
                         'osu_reduce_scatter', 'osu_bcast', 'osu_ireduce', 'osu_ialltoallv', 'osu_barrier',
                         'osu_alltoallv', 'osu_igather', 'osu_allgatherv', 'osu_iscatter', 'osu_igatherv',
                         'osu_gatherv', 'osu_iscatterv', 'osu_ireduce_scatter', 'osu_ibcast', 'osu_scatter',
                         'osu_allgather', 'osu_iallgatherv', 'osu_ibarrier'
    ]
    for exe in wl_mpi_collective:
        workload(exe, executables=['run_mpi'])

    wl_mpi_collective_n = ['osu_ineighbor_allgather', 'osu_ineighbor_alltoall', 'osu_ineighbor_alltoallw',
                           'osu_neighbor_allgather', 'osu_ineighbor_alltoallv', 'osu_neighbor_alltoall',
                           'osu_neighbor_allgatherv', 'osu_neighbor_alltoallv', 'osu_ineighbor_allgatherv',
                           'osu_neighbor_alltoallw'
    ]
    for exe in wl_mpi_collective_n:
        workload(exe, executables=['run_mpi4'])

    wl_mpi_onesided = ['osu_put_bw', 'osu_fop_latency', 'osu_put_bibw', 'osu_get_bw', 'osu_cas_latency',
                       'osu_get_latency', 'osu_put_latency', 'osu_acc_latency', 'osu_get_acc_latency'
    ]
    for exe in wl_mpi_onesided:
        workload(exe, executables=['run_mpi'])

    wl_mpi_congestion = ['osu_bw_fan_in', 'osu_bw_fan_out']
    for exe in wl_mpi_congestion:
        workload(exe, executables=['run_mpi'])

    wl_mpi_startup = ['osu_hello', 'osu_init']
    for exe in wl_mpi_startup:
        workload(exe, executables=['run_mpi'])

    wl_xccl_pt2pt = ['osu_xccl_latency', 'osu_xccl_bibw', 'osu_xccl_bw']
    for exe in wl_xccl_pt2pt:
        workload(exe, executables=['run_mpi'])

    wl_xccl_collective = ['osu_xccl_reduce_scatter', 'osu_xccl_alltoall', 'osu_xccl_allgather', 'osu_xccl_reduce', 'osu_xccl_bcast', 
                          'osu_xccl_allreduce'
    ]
    for exe in wl_xccl_collective:
        workload(exe, executables=['run_mpi'])

    wl_oshm = ['osu_oshm_broadcast', 'osu_oshm_reduce', 'osu_oshm_collect', 'osu_oshm_barrier', 'osu_oshm_fcollect']
    for exe in wl_oshm:
        workload(exe, executables=['run_mpi'])

    wl_oshm_mem = ['osu_oshm_put_bw', 'osu_oshm_get_nb', 'osu_oshm_put_mr_nb', 'osu_oshm_get_nb_bw',
                   'osu_oshm_get_overlap', 'osu_oshm_get_bw', 'osu_oshm_put_nb_bw', 'osu_oshm_get_mr_nb', 'osu_oshm_put_overlap',
                   'osu_oshm_get', 'osu_oshm_put', 'osu_oshm_put_nb', 'osu_oshm_atomics', 'osu_oshm_put_mr'
    ]
    for exe in wl_oshm_mem:
        workload(exe, executables=['run_mpi'])

    # workload_variables
#    workload_variable('benchmark_name', default='{workload_name}',
#                      description='Name of the OSU benchmark binary',
#                      workloads=['osu_bibw', 'osu_bw', 'osu_latency',
#                                 'osu_latency_mp', 'osu_latency_mt',
#                                 'osu_mbw_mr', 'osu_multi_lat'])
    workload_variable('benchmark_name', default='{workload_name}',
                      description='Name of the OSU benchmark binary',
                      workloads=wl_mpi_pt2pt+wl_mpi_pt2pt_p+wl_mpi_collective+wl_mpi_collective_n+wl_mpi_onesided
                                +wl_mpi_congestion+wl_mpi_startup+wl_xccl_pt2pt+wl_xccl_collective+wl_oshm
                     )
    workload_variable('benchmark_name', default='{workload_name} {oshm_mem_type}',
                      description='Name of the OSU benchmark binary with memory type',
                      workloads=wl_oshm_mem
                     )

    workload_variable('oshm_mem_type', default='heap',
                      description='OSHM memory type: heap or global',
                      workloads=wl_oshm_mem
                     )

    workload_variable('export_environments', default='OMPI_MCA_coll="^hcoll,ucc" OMPI_MCA_pml=ob1 OMPI_MCA_btl=vader,self,tcp OMPI_MCA_btl_tcp_timeout=5 ',
                      description='special setting for osu_latency_mt',
                      workloads=['osu_latency_mt']
                     )


