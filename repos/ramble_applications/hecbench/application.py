# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import os

from ramble.appkit import *
from ramble.expander import Expander


class Hecbench(ExecutableApplication):
    """HeCBench, the heterogeneous computing benchmark suite, driven as a
    single Benchpark application.

    HeCBench is a collection of several hundred GPU kernels implemented in
    CUDA, HIP, SYCL and OpenMP target offloading.  Rather than exposing every
    kernel as its own Benchpark application, the whole collection is run by one
    driver (`hecbench-run`, installed by the `hecbench` Spack package).  The
    driver executes every benchmark of the selected programming model with the
    arguments HeCBench itself defines, extracts each benchmark's own timing
    metric, and prints one uniform line per benchmark followed by a summary.

    Figures of merit are therefore reported at two levels:
      * per benchmark, in the `benchmark` context (kernel time, reported
        metric, wall time, status);
      * for the suite as a whole (pass rate, geometric mean kernel time, total
        kernel time, throughput).
    """

    name = "hecbench"

    maintainers("ando")

    tags(
        "benchmark-suite",
        "gpu",
        "microbenchmark",
        "cuda",
        "hip",
        "sycl",
        "openmp-target",
        "single-node",
        "sub-node",
        "c++",
    )

    executable(
        "execute",
        "hecbench-run"
        " --model {hecbench_model}"
        " --select {hecbench_select}"
        " --repeat {hecbench_repeat}"
        " --timeout-scale {hecbench_timeout_scale}"
        " --results {experiment_run_dir}/hecbench-results.json",
        use_mpi=False,
    )

    workload("hecbench", executables=["execute"])

    workload_variable(
        "hecbench_model",
        default="cuda",
        description="HeCBench programming model to run: cuda, hip, sycl or omp",
        workloads=["hecbench"],
    )
    workload_variable(
        "hecbench_select",
        default="runnable",
        description="Which benchmarks to run: 'runnable' for every benchmark "
        "HeCBench provides run arguments and a result pattern for, "
        "'category:<c1,c2>' for whole categories, or a comma separated list of "
        "benchmark names",
        workloads=["hecbench"],
    )
    workload_variable(
        "hecbench_repeat",
        default="1",
        description="Number of runs per benchmark; the best result is reported",
        workloads=["hecbench"],
    )
    workload_variable(
        "hecbench_timeout_scale",
        default="1.0",
        description="Multiplier applied to each benchmark's upstream timeout",
        workloads=["hecbench"],
    )

    log_file = os.path.join(
        Expander.expansion_str("experiment_run_dir"),
        Expander.expansion_str("experiment_name") + ".out",
    )

    # ------------------------------------------------------------------
    # Per-benchmark figures of merit
    # ------------------------------------------------------------------
    # Matches every result line, including the ones for benchmarks that did
    # not produce a metric.
    result_regex = (
        r"\[hecbench\] benchmark=(?P<bench>\S+)"
        r" model=(?P<model>\S+)"
        r" status=(?P<status>\S+)"
        r" metric=(?P<metric>\S+)"
        r" kernel_time=(?P<kernel_time>\S+)"
        r" walltime=(?P<walltime>[0-9eE.+-]+)"
    )

    # Matches only the lines that carry a numeric metric, so that a failed
    # benchmark reports no timing figure of merit rather than a bogus one.
    timed_regex = (
        r"\[hecbench\] benchmark=(?P<bench>\S+)"
        r" model=(?P<model>\S+)"
        r" status=(?P<status>\S+)"
        r" metric=(?P<metric>[0-9][0-9eE.+-]*)"
        r" kernel_time=(?P<kernel_time>[0-9][0-9eE.+-]*)"
        r" walltime=(?P<walltime>[0-9eE.+-]+)"
    )

    figure_of_merit_context(
        "benchmark",
        regex=r"\[hecbench\] benchmark=(?P<bench>\S+) model=(?P<model>\S+)",
        output_format="{bench}",
    )

    figure_of_merit(
        "Kernel time",
        log_file=log_file,
        fom_regex=timed_regex,
        group_name="kernel_time",
        units="s",
        contexts=["benchmark"],
        fom_type=FomType.TIME,
    )

    figure_of_merit(
        "Reported metric",
        log_file=log_file,
        fom_regex=timed_regex,
        group_name="metric",
        units="",
        contexts=["benchmark"],
        fom_type=FomType.MEASURE,
    )

    figure_of_merit(
        "Benchmark walltime",
        log_file=log_file,
        fom_regex=result_regex,
        group_name="walltime",
        units="s",
        contexts=["benchmark"],
        fom_type=FomType.TIME,
    )

    figure_of_merit(
        "Benchmark status",
        log_file=log_file,
        fom_regex=result_regex,
        group_name="status",
        units="",
        contexts=["benchmark"],
        fom_type=FomType.CATEGORY,
    )

    # ------------------------------------------------------------------
    # Suite level figures of merit
    # ------------------------------------------------------------------
    figure_of_merit(
        "Figure of Merit (FOM)",
        log_file=log_file,
        fom_regex=r"HeCBench geometric mean kernel time:\s+(?P<geomean>[0-9eE.+-]+)\s+s",
        group_name="geomean",
        units="s",
        fom_type=FomType.TIME,
    )

    figure_of_merit(
        "Geometric mean kernel time",
        log_file=log_file,
        fom_regex=r"HeCBench geometric mean kernel time:\s+(?P<geomean>[0-9eE.+-]+)\s+s",
        group_name="geomean",
        units="s",
        fom_type=FomType.TIME,
    )

    figure_of_merit(
        "Total kernel time",
        log_file=log_file,
        fom_regex=r"HeCBench total kernel time:\s+(?P<total>[0-9eE.+-]+)\s+s",
        group_name="total",
        units="s",
        fom_type=FomType.TIME,
    )

    figure_of_merit(
        "Suite walltime",
        log_file=log_file,
        fom_regex=r"HeCBench suite walltime:\s+(?P<walltime>[0-9eE.+-]+)\s+s",
        group_name="walltime",
        units="s",
        fom_type=FomType.TIME,
    )

    figure_of_merit(
        "Suite throughput",
        log_file=log_file,
        fom_regex=r"HeCBench throughput:\s+(?P<rate>[0-9eE.+-]+)\s+benchmarks/s",
        group_name="rate",
        units="benchmarks/s",
        fom_type=FomType.THROUGHPUT,
    )

    figure_of_merit(
        "Benchmarks attempted",
        log_file=log_file,
        fom_regex=r"HeCBench benchmarks attempted:\s+(?P<count>[0-9]+)",
        group_name="count",
        units="",
        fom_type=FomType.MEASURE,
    )

    figure_of_merit(
        "Benchmarks passed",
        log_file=log_file,
        fom_regex=r"HeCBench benchmarks passed:\s+(?P<count>[0-9]+)",
        group_name="count",
        units="",
        fom_type=FomType.MEASURE,
    )

    figure_of_merit(
        "Benchmarks failed",
        log_file=log_file,
        fom_regex=r"HeCBench benchmarks failed:\s+(?P<count>[0-9]+)",
        group_name="count",
        units="",
        fom_type=FomType.MEASURE,
    )

    figure_of_merit(
        "Benchmarks skipped",
        log_file=log_file,
        fom_regex=r"HeCBench benchmarks skipped:\s+(?P<count>[0-9]+)",
        group_name="count",
        units="",
        fom_type=FomType.MEASURE,
    )

    figure_of_merit(
        "Pass rate",
        log_file=log_file,
        fom_regex=r"HeCBench pass rate:\s+(?P<rate>[0-9.]+)\s+%",
        group_name="rate",
        units="%",
        fom_type=FomType.MEASURE,
    )

    figure_of_merit(
        "Programming model",
        log_file=log_file,
        fom_regex=r"HeCBench model:\s+(?P<model>\S+)",
        group_name="model",
        units="",
        fom_type=FomType.CATEGORY,
    )

    figure_of_merit(
        "Suite status",
        log_file=log_file,
        fom_regex=r"HeCBench status:\s+(?P<status>\S+)",
        group_name="status",
        units="",
        fom_type=FomType.CATEGORY,
    )

    # ------------------------------------------------------------------
    # Success criteria
    # ------------------------------------------------------------------
    success_criteria(
        "suite-completed",
        mode="string",
        match=r"### HeCBench summary",
        file=log_file,
    )

    success_criteria(
        "suite-not-failed",
        mode="string",
        anti_match=r"HeCBench status: FAILED",
        file=log_file,
    )

    success_criteria(
        "fom-produced",
        mode="fom_comparison",
        fom_name="Benchmarks passed",
        formula="{value} > 0",
    )
