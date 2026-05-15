# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from benchpark.directives import variant
from benchpark.experiment import Experiment
from benchpark.programming_model import ProgrammingModel, ProgrammingModelType


class SalmonTddft(
    Experiment,
    ProgrammingModel(
        ProgrammingModelType.Mpionly, 
        ProgrammingModelType.Openmp,
    ),
):

    variant(
        "workload",
        default="Si-1-1-1",
        # values=("Si-1-1-1", "Si-2-2-2", "Si-3-3-3"),
        multi=True,
        description="salmon-tddft",
    )

    variant(
        "version",
        default="2.2.2",
        description="app version",
    )

    def compute_applications_section(self):
        self.add_experiment_variable("processes_per_node", ["4"], True)
        self.add_experiment_variable("omp_num_threads", ["12"], True)
        self.add_experiment_variable("n_nodes", ["1"], True)

        self.add_experiment_variable("n_ranks", "{processes_per_node} * {n_nodes}", True)
        self.add_experiment_variable("size", 44051, True)   # Defined by rgrid in input
        
        self.set_required_variables(
            n_resources="{n_ranks}", 
            process_problem_size="{size}/{n_ranks}", 
            total_problem_size="{size}"
        )

    def compute_package_section(self):
        self.add_package_spec(self.name, [f"salmon-tddft{self.determine_version()}"])

