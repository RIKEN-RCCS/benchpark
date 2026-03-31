# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from benchpark.experiment import Experiment
from benchpark.programming_model import ProgrammingModel, ProgrammingModelType
from benchpark.directives import variant, maintainers

class Ffb(
    Experiment,
    ProgrammingModel(
        ProgrammingModelType.Mpionly,
    ),
):
    variant(
        "workload",
        default="cavity",
        description="ffb",
    )

    variant(
        "version",
        default="67.01",
        description="Which benchmark version to use.",
    )

    maintainers("ando")

    def compute_applications_section(self):
        has_cuda = self.system_spec.satisfies("compiler=cuda")

        if has_cuda: # GPU
            self.add_experiment_variable("n_nodes", 4, True)
            self.add_experiment_variable("processes_per_node", 1)
            self.add_experiment_variable("n_ranks", "{processes_per_node} * {n_nodes}")
            self.add_experiment_variable("size", 31255875, True)
            self.add_experiment_variable("extra_batch_opts", "-N 4", named=False)
        else: # CPU
            self.add_experiment_variable("n_nodes", ["4"], True)
            self.add_experiment_variable("processes_per_node", ["4"])
            self.add_experiment_variable("n_ranks", "{processes_per_node} * {n_nodes}")
            self.add_experiment_variable("omp_num_threads", ["12"])
            self.add_experiment_variable("size", 8493380, True)

        self.set_required_variables(
            n_resources="{n_ranks}",
            process_problem_size="{size}/{n_ranks}",
            total_problem_size="{size}",
        )

    def compute_package_section(self):
        base_version = self.spec.variants['version'][0]

        suffix = "-gpu" if self.system_spec.satisfies("compiler=cuda") else "-cpu"
        spec_str = f"ffb@{base_version}{suffix}"
        self.add_package_spec(self.name, [spec_str])

