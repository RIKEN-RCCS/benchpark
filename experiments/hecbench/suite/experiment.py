# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from benchpark.directives import maintainers, variant
from benchpark.experiment import Experiment
from benchpark.programming_model import ProgrammingModel, ProgrammingModelType


class Suite(
    Experiment,
    ProgrammingModel(
        ProgrammingModelType.Cuda,
        ProgrammingModelType.Rocm,
        ProgrammingModelType.Openmp,
    ),
):
    """HeCBench run as a suite (hecbench.suite).

    Many HeCBench benchmarks of one programming model (CUDA, HIP or OpenMP
    target offloading) are built by one install and executed by one run.
    The run reports a figure of merit for every benchmark and aggregates them
    into suite-level figures of merit. The single-benchmark experiments of
    this namespace (hecbench.softmax, hecbench.nbody, hecbench.wmma) build
    and run one benchmark each.

    Examples:
        benchpark experiment init --dest=suite <system> hecbench.suite+cuda
        benchpark experiment init --dest=suite <system> hecbench.suite+cuda benchmarks=smoke
        benchpark experiment init --dest=suite <system> hecbench.suite+openmp
    """

    variant(
        "workload",
        default="hecbench",
        description="hecbench",
    )

    variant(
        "version",
        # A fixed commit, so that a result can be reproduced; master follows
        # upstream and changes the set of benchmarks built from day to day.
        default="2026-10-28",
        values=("master", "2026-10-28", "2026-08-16"),
        description="app version",
    )

    variant(
        "benchmarks",
        default="runnable",
        values=("smoke", "runnable", "all"),
        description="Which part of the suite to build: 'smoke' for a small "
        "representative set, 'runnable' for every benchmark HeCBench provides "
        "run arguments and a result pattern for, or 'all' for every benchmark "
        "of the selected programming model",
    )

    variant(
        "select",
        default="runnable",
        description="Benchmarks to execute: 'runnable', 'category:<c1,c2>' or "
        "a comma separated list of benchmark names",
    )

    variant(
        "repeat",
        default="1",
        description="Number of runs per benchmark; the best result is reported",
    )

    variant(
        "timeout_scale",
        default="1.0",
        description="Multiplier applied to each benchmark's upstream timeout",
    )

    maintainers("ando")

    def __init__(self, spec):
        super().__init__(spec)
        self.name = "suite"

    # Number of benchmarks HeCBench currently provides run metadata for. It is
    # only used to express the problem size of the suite; the driver discovers
    # the real list at run time.
    n_benchmarks = 163

    def hecbench_model(self):
        """Map the Benchpark programming model onto HeCBench's own naming."""
        if self.spec.satisfies("+cuda"):
            return "cuda"
        if self.spec.satisfies("+rocm"):
            return "hip"
        return "omp"

    def compute_applications_section(self):
        # Every HeCBench benchmark is a single-process, single-device kernel
        # driver, so the suite runs in one process on one node.
        self.add_experiment_variable("n_nodes", 1, True)

        self.add_experiment_variable("hecbench_model", self.hecbench_model(), False)
        self.add_experiment_variable(
            "hecbench_select", self.spec.variants["select"][0], False
        )
        self.add_experiment_variable(
            "hecbench_repeat", self.spec.variants["repeat"][0], False
        )
        self.add_experiment_variable(
            "hecbench_timeout_scale", self.spec.variants["timeout_scale"][0], False
        )
        self.add_experiment_variable("n_benchmarks", self.n_benchmarks, False)

        if self.spec.satisfies("+cuda") or self.spec.satisfies("+rocm"):
            self.add_experiment_variable("n_gpus", 1, True)
            n_resources = "{n_gpus}"
        else:
            self.add_experiment_variable("n_ranks", 1, True)
            n_resources = "{n_ranks}"

        self.set_required_variables(
            n_resources=n_resources,
            process_problem_size="{n_benchmarks}/" + n_resources,
            total_problem_size="{n_benchmarks}",
        )

    def compute_package_section(self):
        spack_specs = (
            f"benchmark=suite benchmarks={self.spec.variants['benchmarks'][0]} "
        )

        self.add_package_spec(
            self.name,
            [f"hecbench{self.determine_version()} {spack_specs}"],
        )
