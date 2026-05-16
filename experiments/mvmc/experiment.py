# Copyright 2026
# SPDX-License-Identifier: Apache-2.0

from benchpark.directives import maintainers, variant
from benchpark.experiment import Experiment
from benchpark.programming_model import ProgrammingModel, ProgrammingModelType


class Mvmc(
    Experiment,
    ProgrammingModel(ProgrammingModelType.Mpionly),
):
    """Minimal mVMC experiment for Fugaku bring-up."""

    variant(
        "workload",
        default="standard",
        description="Which Ramble workload to execute.",
    )

    variant(
        "version",
        default="1.3.0",
        values=("1.3.0", "master", "latest"),
        description="Which mVMC version to use.",
    )

    maintainers("otsukay")

    def compute_applications_section(self):
        self.add_experiment_variable("n_nodes", 1, True)
        self.add_experiment_variable("n_ranks", 1, True)

        self.add_experiment_variable(
            "n_threads_per_proc", ["1"], named=True, matrixed=True
        )

        # mVMC Standard mode input: Heisenberg chain minimal sample.
        self.add_experiment_variable("L", 16, True)
        self.add_experiment_variable("Lsub", 4, False)
        self.add_experiment_variable("model", "Spin", False)
        self.add_experiment_variable("lattice", "chain lattice", False)
        self.add_experiment_variable("J", "1.0", False)
        self.add_experiment_variable("two_sz", 0, False)
        self.add_experiment_variable("nmptrans", 1, False)

        self.set_required_variables(
            n_resources="{n_ranks}",
            process_problem_size="{L}/{n_ranks}",
            total_problem_size="{L}",
        )

    def compute_package_section(self):
        self.add_package_spec(self.name, [f"mvmc{self.determine_version()}"])

