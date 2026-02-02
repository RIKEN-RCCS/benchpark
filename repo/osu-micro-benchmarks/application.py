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

    workload_variable('benchmark_name', default='{workload_name}',
                      description='Name of the OSU benchmark binary',
                      workloads=['osu_bibw', 'osu_bw', 'osu_latency',
                                 'osu_latency_mp', 'osu_latency_mt',
                                 'osu_mbw_mr', 'osu_multi_lat'])

