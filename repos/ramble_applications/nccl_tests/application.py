# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from ramble.app.builtin.nccl_tests import NcclTests as NcclTestsBase
from ramble.appkit import *


class NcclTests(NcclTestsBase):
    """ramble's nccl-tests plus the benchmarks it does not list (added with
    the RIKEN-RCCS work): broadcast, gather, reduce, scatter, hypercube."""

    riken_workloads = ["broadcast", "gather", "reduce", "scatter", "hypercube"]

    for benchmark in riken_workloads:
        executable(
            f"{benchmark}-execute",
            template=[f"{benchmark}_perf " + "{additional_args}"],
            use_mpi=True,
        )
        workload(benchmark, executables=[f"{benchmark}-execute"])

    all_workloads = NcclTestsBase.all_workloads + riken_workloads

    # The same variables the builtin workloads have, so {additional_args}
    # expands for the added ones too.
    workload_variable(
        "num_gpus_per_task",
        default="1",
        description="Number of GPUs per task",
        workloads=riken_workloads,
    )
    workload_variable(
        "begin_message_size",
        default="8",
        description="Beginning message size",
        workloads=riken_workloads,
    )
    workload_variable(
        "end_message_size",
        default="8G",
        description="Ending message size",
        workloads=riken_workloads,
    )
    workload_variable(
        "message_size_factor",
        default="2",
        description="Factor used in size sweep",
        workloads=riken_workloads,
    )
    workload_variable(
        "warmup_iters",
        default="5",
        description="Number of warmup iterations",
        workloads=riken_workloads,
    )
    workload_variable(
        "num_iters",
        default="100",
        description="Number of iterations to perform",
        workloads=riken_workloads,
    )
    workload_variable(
        "result_check",
        default="1",
        description="0 to skip checking, 1 to enable checking",
        workloads=riken_workloads,
    )
    workload_variable(
        "additional_args",
        default="-b {begin_message_size} -e {end_message_size} -f {message_size_factor} -g {num_gpus_per_task} -w {warmup_iters} --iters {num_iters} -c {result_check}",
        description="Arguments for the benchmark",
        workloads=riken_workloads,
    )
    workload_variable(
        "nccl_tests_split_mask",
        default="",
        description='How NCCL communicators should be split, if at all. "0x7" for rail-aligned, "0x0" for world-level.',
        workloads=riken_workloads,
        environment_variable_name="NCCL_TESTS_SPLIT_MASK",
        expandable=False,
    )
