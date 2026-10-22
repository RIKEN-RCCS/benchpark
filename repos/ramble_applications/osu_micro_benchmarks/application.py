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

    # Benchmarks OMB 7.5 builds that ramble's application does not name
    # (added with the RIKEN-RCCS work). Same shape as the builtin ones: the
    # binary, then {additional_args}, launched by {mpi_command}.
    riken_workloads = [
        # point-to-point and one-sided
        "osu_acc_latency",
        "osu_latency_persistent",
        "osu_bw_persistent",
        "osu_bibw_persistent",
        # network congestion
        "osu_bw_fan_in",
        "osu_bw_fan_out",
        # NCCL/RCCL (built with +xccl)
        "osu_xccl_latency",
        "osu_xccl_bw",
        "osu_xccl_bibw",
        "osu_xccl_allgather",
        "osu_xccl_allreduce",
        "osu_xccl_alltoall",
        "osu_xccl_bcast",
        "osu_xccl_reduce",
        "osu_xccl_reduce_scatter",
    ]

    # OpenSHMEM collectives (built with +openshmem)
    oshm_workloads = [
        "osu_oshm_barrier",
        "osu_oshm_broadcast",
        "osu_oshm_collect",
        "osu_oshm_fcollect",
        "osu_oshm_reduce",
    ]

    # OpenSHMEM benchmarks that take the memory kind of their buffers
    # (heap or global) as their first argument
    oshm_mem_workloads = [
        "osu_oshm_atomics",
        "osu_oshm_get",
        "osu_oshm_get_bw",
        "osu_oshm_get_mr_nb",
        "osu_oshm_get_nb",
        "osu_oshm_get_nb_bw",
        "osu_oshm_get_overlap",
        "osu_oshm_put",
        "osu_oshm_put_bw",
        "osu_oshm_put_mr",
        "osu_oshm_put_mr_nb",
        "osu_oshm_put_nb",
        "osu_oshm_put_nb_bw",
        "osu_oshm_put_overlap",
    ]

    for benchmark in riken_workloads + oshm_workloads:
        executable(
            name=f"execute-{benchmark}",
            template=f"{benchmark} " + "{additional_args}",
            use_mpi=True,
        )
        workload(benchmark, executable=f"execute-{benchmark}")

    for benchmark in oshm_mem_workloads:
        executable(
            name=f"execute-{benchmark}",
            template=f"{benchmark} " + "{oshm_mem_type} {additional_args}",
            use_mpi=True,
        )
        workload(benchmark, executable=f"execute-{benchmark}")

    # The builtin workloads default to -z (tail statistics). Of the ones
    # added here only the point-to-point benchmarks accept it; the one-sided,
    # xccl and OpenSHMEM option sets do not.
    workload_variable(
        "additional_args",
        default="-z",
        description="Additional arguments for benchmark",
        workloads=["osu_latency_persistent", "osu_bw_persistent", "osu_bibw_persistent"],
    )
    workload_variable(
        "additional_args",
        default="",
        description="Additional arguments for benchmark",
        workloads=[
            w
            for w in riken_workloads
            if w not in ("osu_latency_persistent", "osu_bw_persistent", "osu_bibw_persistent")
        ]
        + oshm_workloads
        + oshm_mem_workloads,
    )

    workload_variable(
        "oshm_mem_type",
        default="heap",
        description="OpenSHMEM memory the buffers come from: heap or global",
        workloads=oshm_mem_workloads,
    )
