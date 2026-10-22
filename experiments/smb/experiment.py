# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from benchpark.directives import maintainers, variant
from benchpark.experiment import Experiment
from benchpark.programming_model import ProgrammingModel, ProgrammingModelType


class Smb(
    Experiment,
    ProgrammingModel(ProgrammingModelType.Mpionly),
):
    variant(
        "workload",
        default="mpi_overhead",
        values=("mpi_overhead", "msgrate", "rma_mt", "rma_mt_mpi"),
        description="workload",
    )

    variant(
        "version",
        default="1.1",
        values=("master", "latest", "1.1"),
        description="app version",
    )

    variant(
        "threads",
        default="1",
        description="rma_mt_mpi: threads doing communication per rank (-t)",
    )
    variant(
        "iterations",
        default="4096",
        description="rma_mt_mpi: iterations per test (-i); each one invalidates the cache "
        "and exchanges every message, so the default takes hours on a full node",
    )
    variant(
        "ranks",
        default="none",
        description="rma_mt_mpi: ranks on the node; the default is half the cores, which "
        "can be more one-sided windows than the NICs have resources for",
    )

    maintainers("nhanford")

    def compute_applications_section(self):
        if self.spec.satisfies("workload=mpi_overhead"):
            self.add_experiment_variable("n_ranks", "2")
        elif self.spec.satisfies("workload=msgrate") or self.spec.satisfies(
            "workload=rma_mt"
        ):
            self.add_experiment_variable("n_nodes", "1")
            self.add_experiment_variable("n_ranks", "{n_nodes}*{sys_cores_per_node}")
        elif self.spec.satisfies("workload=rma_mt_mpi"):
            # The multi-threaded RMA message-rate test: half the cores take
            # a rank each, the other half the threads (RIKEN-RCCS addition).
            # It asks for MPI_THREAD_MULTIPLE; a system whose MPI needs a
            # thread-safe stack for that has to provide it.
            self.add_experiment_variable("n_nodes", "1")
            ranks = self.spec.variants["ranks"][0]
            self.add_experiment_variable(
                "n_ranks", "{n_nodes}*{sys_cores_per_node}//2" if ranks == "none" else ranks
            )
            self.add_experiment_variable("threads", self.spec.variants["threads"][0])
            self.add_experiment_variable("iterations", self.spec.variants["iterations"][0])

        self.set_required_variables(
            n_resources="{n_ranks}", process_problem_size="", total_problem_size=""
        )

    def compute_package_section(self):
        spec_string = f"smb{self.determine_version()}"
        if self.spec.satisfies("workload=rma_mt") or self.spec.satisfies(
            "workload=rma_mt_mpi"
        ):
            spec_string += "+rma"
        self.add_package_spec(self.name, [spec_string])
