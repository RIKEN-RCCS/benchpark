# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from benchpark.directives import maintainers, variant
from benchpark.experiment import Experiment
from benchpark.programming_model import ProgrammingModel, ProgrammingModelType


class Hecbench(
    Experiment,
    ProgrammingModel(
        ProgrammingModelType.Cuda,
        ProgrammingModelType.Rocm,
        ProgrammingModelType.Openmp,
    ),
):
    """HeCBench run as a single Benchpark application.

    The whole HeCBench collection (several hundred GPU kernels in CUDA, HIP,
    SYCL and OpenMP target offloading) is built and executed as one benchmark.
    A single run walks the suite, reports a figure of merit for every
    individual benchmark and aggregates them into suite level figures of merit.

    Examples:
        benchpark experiment init --dest=hecbench hecbench +cuda
        benchpark experiment init --dest=hecbench hecbench +cuda benchmarks=all
        benchpark experiment init --dest=hecbench hecbench +openmp
    """

    variant(
        "workload",
        default="hecbench",
        description="hecbench",
    )

    variant(
        "version",
        default="master",
        values=("master", "2026.08.16"),
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
        spack_specs = f"benchmarks={self.spec.variants['benchmarks'][0]} "

        self.add_package_spec(
            self.name,
            [f"hecbench{self.determine_version()} {spack_specs}"],
        )
