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
    #executable('run_mpi', '{benchmark_name} {additional_args}', use_mpi=True)
    executable('run_mpi', '{pre_run_cmds}\n{mpi_command} {benchmark_name} {additional_args}', use_mpi=True)

    workload('osu_bibw', executables=['run_mpi'])
    workload('osu_bw', executables=['run_mpi'])
    workload('osu_latency', executables=['run_mpi'])
    workload('osu_latency_mp', executables=['run_mpi'])
    workload('osu_latency_mt', executables=['run_mpi'])
    workload('osu_mbw_mr', executables=['run_mpi'])
    workload('osu_multi_lat', executables=['run_mpi'])
    wl_mpi_pt2pt=['osu_bibw', 'osu_bw', 'osu_latency', 'osu_latency_mp', 'osu_latency_mt',
                  'osu_mbw_mr', 'osu_multi_lat'
    ]

    workload('osu_alltoallw', executables=['run_mpi'])
    workload('osu_allreduce', executables=['run_mpi'])
    workload('osu_reduce', executables=['run_mpi'])
    workload('osu_iallgather', executables=['run_mpi'])
    workload('osu_alltoall', executables=['run_mpi'])
    workload('osu_scatterv', executables=['run_mpi'])
    workload('osu_ialltoallw', executables=['run_mpi'])
    workload('osu_iallreduce', executables=['run_mpi'])
    workload('osu_ineighbor_alltoall', executables=['run_mpi'])
    workload('osu_gather', executables=['run_mpi'])
    workload('osu_ineighbor_alltoallw', executables=['run_mpi'])
    workload('osu_ialltoall', executables=['run_mpi'])
    workload('osu_neighbor_allgather', executables=['run_mpi'])
    workload('osu_reduce_scatter', executables=['run_mpi'])
    workload('osu_bcast', executables=['run_mpi'])
    workload('osu_ineighbor_alltoallv', executables=['run_mpi'])
    workload('osu_ireduce', executables=['run_mpi'])
    workload('osu_neighbor_alltoall', executables=['run_mpi'])
    workload('osu_neighbor_allgatherv', executables=['run_mpi'])
    workload('osu_neighbor_alltoallv', executables=['run_mpi'])
    workload('osu_ialltoallv', executables=['run_mpi'])
    workload('osu_barrier', executables=['run_mpi'])
    workload('osu_alltoallv', executables=['run_mpi'])
    workload('osu_igather', executables=['run_mpi'])
    workload('osu_allgatherv', executables=['run_mpi'])
    workload('osu_ineighbor_allgatherv', executables=['run_mpi'])
    workload('osu_iscatter', executables=['run_mpi'])
    workload('osu_igatherv', executables=['run_mpi'])
    workload('osu_gatherv', executables=['run_mpi'])
    workload('osu_iscatterv', executables=['run_mpi'])
    workload('osu_ireduce_scatter', executables=['run_mpi'])
    workload('osu_ineighbor_allgather', executables=['run_mpi'])
    workload('osu_ibcast', executables=['run_mpi'])
    workload('osu_neighbor_alltoallw', executables=['run_mpi'])
    workload('osu_ibarrier', executables=['run_mpi'])
    workload('osu_scatter', executables=['run_mpi'])
    workload('osu_allgather', executables=['run_mpi'])
    workload('osu_iallgatherv', executables=['run_mpi'])
    wl_mpi_collective=['osu_alltoallw', 'osu_allreduce', 'osu_reduce', 'osu_iallgather', 'osu_alltoall',
                       'osu_scatterv', 'osu_ialltoallw', 'osu_iallreduce', 'osu_ineighbor_alltoall', 'osu_gather',
                       'osu_ineighbor_alltoallw', 'osu_ialltoall', 'osu_neighbor_allgather', 'osu_reduce_scatter', 'osu_bcast',
                       'osu_ineighbor_alltoallv', 'osu_ireduce', 'osu_neighbor_alltoall', 'osu_neighbor_allgatherv', 'osu_neighbor_alltoallv',
                       'osu_ialltoallv', 'osu_barrier', 'osu_alltoallv', 'osu_igather', 'osu_allgatherv',
                       'osu_ineighbor_allgatherv', 'osu_iscatter', 'osu_igatherv', 'osu_gatherv', 'osu_iscatterv',
                       'osu_ireduce_scatter', 'osu_ineighbor_allgather', 'osu_ibcast', 'osu_neighbor_alltoallw', 'osu_ibarrier',
                       'osu_scatter', 'osu_allgather', 'osu_iallgatherv'
    ]

    workload('osu_put_bw', executables=['run_mpi'])
    workload('osu_fop_latency', executables=['run_mpi'])
    workload('osu_put_bibw', executables=['run_mpi'])
    workload('osu_get_bw', executables=['run_mpi'])
    workload('osu_cas_latency', executables=['run_mpi'])
    workload('osu_get_latency', executables=['run_mpi'])
    workload('osu_put_latency', executables=['run_mpi'])
    workload('osu_acc_latency', executables=['run_mpi'])
    workload('osu_get_acc_latency', executables=['run_mpi'])
    wl_mpi_onesided=['osu_put_bw', 'osu_fop_latency', 'osu_put_bibw', 'osu_get_bw', 'osu_cas_latency',
                     'osu_get_latency', 'osu_put_latency', 'osu_acc_latency', 'osu_get_acc_latency'
    ]

    workload('osu_bw_fan_in', executables=['run_mpi'])
    workload('osu_bw_fan_out', executables=['run_mpi'])
    wl_mpi_congestion=['osu_bw_fan_in', 'osu_bw_fan_out']

    workload('osu_hello', executables=['run_mpi'])
    workload('osu_init', executables=['run_mpi'])
    wl_mpi_startup=['osu_hello', 'osu_init']

    workload('osu_xccl_latency', executables=['run_mpi'])
    workload('osu_xccl_bibw', executables=['run_mpi'])
    workload('osu_xccl_bw', executables=['run_mpi'])
    wl_xccl_pt2pt=['osu_xccl_latency', 'osu_xccl_bibw', 'osu_xccl_bw']

    workload('osu_xccl_reduce_scatter', executables=['run_mpi'])
    workload('osu_xccl_alltoall', executables=['run_mpi'])
    workload('osu_xccl_allgather', executables=['run_mpi'])
    workload('osu_xccl_reduce', executables=['run_mpi'])
    workload('osu_xccl_bcast', executables=['run_mpi'])
    workload('osu_xccl_allreduce', executables=['run_mpi'])
    wl_xccl_collective=['osu_xccl_reduce_scatter', 'osu_xccl_alltoall', 'osu_xccl_allgather', 'osu_xccl_reduce', 'osu_xccl_bcast', 
                        'osu_xccl_allreduce'
    ]

    workload('osu_oshm_put_bw', executables=['run_mpi'])
    workload('osu_oshm_get_nb', executables=['run_mpi'])
    workload('osu_oshm_put_mr_nb', executables=['run_mpi'])
    workload('osu_oshm_get_nb_bw', executables=['run_mpi'])
    workload('osu_oshm_broadcast', executables=['run_mpi'])
    workload('osu_oshm_get_overlap', executables=['run_mpi'])
    workload('osu_oshm_get_bw', executables=['run_mpi'])
    workload('osu_oshm_put_nb_bw', executables=['run_mpi'])
    workload('osu_oshm_get_mr_nb', executables=['run_mpi'])
    workload('osu_oshm_put_overlap', executables=['run_mpi'])
    workload('osu_oshm_reduce', executables=['run_mpi'])
    workload('osu_oshm_get', executables=['run_mpi'])
    workload('osu_oshm_put', executables=['run_mpi'])
    workload('osu_oshm_put_nb', executables=['run_mpi'])
    workload('osu_oshm_collect', executables=['run_mpi'])
    workload('osu_oshm_atomics', executables=['run_mpi'])
    workload('osu_oshm_barrier', executables=['run_mpi'])
    workload('osu_oshm_put_mr', executables=['run_mpi'])
    workload('osu_oshm_fcollect', executables=['run_mpi'])
    wl_oshm=['osu_oshm_put_bw', 'osu_oshm_get_nb', 'osu_oshm_put_mr_nb', 'osu_oshm_get_nb_bw', 'osu_oshm_broadcast',
             'osu_oshm_get_overlap', 'osu_oshm_get_bw', 'osu_oshm_put_nb_bw', 'osu_oshm_get_mr_nb', 'osu_oshm_put_overlap',
             'osu_oshm_reduce', 'osu_oshm_get', 'osu_oshm_put', 'osu_oshm_put_nb', 'osu_oshm_collect',
             'osu_oshm_atomics', 'osu_oshm_barrier', 'osu_oshm_put_mr', 'osu_oshm_fcollect'
    ]

#    workload_variable('benchmark_name', default='{workload_name}',
#                      description='Name of the OSU benchmark binary',
#                      workloads=['osu_bibw', 'osu_bw', 'osu_latency',
#                                 'osu_latency_mp', 'osu_latency_mt',
#                                 'osu_mbw_mr', 'osu_multi_lat'])
    workload_variable('benchmark_name', default='{workload_name}',
                      description='Name of the OSU benchmark binary',
                      workloads=wl_mpi_pt2pt+wl_mpi_collective+wl_mpi_onesided+wl_mpi_congestion+wl_mpi_startup
                                +wl_xccl_pt2pt+wl_xccl_collective+wl_oshm
                     )

