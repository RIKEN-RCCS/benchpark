# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from benchpark.directives import maintainers, variant
from benchpark.experiment import Experiment
from benchpark.programming_model import ProgrammingModel, ProgrammingModelType

#<<<<<<< HEAD
#class Genesis(Experiment, MpiOnlyExperiment, OpenMPExperiment):
#=======

class Genesis(
    Experiment,
    ProgrammingModel(ProgrammingModelType.Mpionly, ProgrammingModelType.Openmp),
):
#>>>>>>> upstream/develop

    variant(
        "workload",
        default="DHFR",
        values=("DHFR", "ApoA1", "UUN", "cryoEM"),
        description="genesis",
    )

    variant(
        "backend",
        default="cpu",
        values=("cpu","gpu"),
        description="genesis backend (cpu or gpu)"
    )

    variant(
        "version",
        default="2.1.6",
        values=("2.1.6", "main"),
        description="app version",
    )

    maintainers("jdomke", "SBA0486")

    def compute_applications_section(self):
        if self.spec.satisfies("exec_mode=test"):
            self.add_experiment_variable("n_nodes", ["1"], True)
        # Must be exec_mode=perf
        else:
            self.add_experiment_variable("n_nodes", ["2"], True)


        if self.spec.satisfies("+openmp"):
            self.add_experiment_variable("n_nodes", ["1"], True)
            self.add_experiment_variable("processes_per_node", ["8"])
            self.add_experiment_variable("n_ranks", "{processes_per_node} * {n_nodes}")
            self.add_experiment_variable("omp_num_threads", ["6"])
            self.add_experiment_variable("arch", "OpenMP")
        else:
            self.add_experiment_variable("n_nodes", ["1"], True)
            self.add_experiment_variable("processes_per_node", ["8"])
            self.add_experiment_variable("n_ranks", "{processes_per_node} * {n_nodes}")
            self.add_experiment_variable("arch", "MPI")

#        if self.spec.variants["backend"][0] == "gpu":
#            self.add_experiment_variable("n_gpus", "{n_nodes}", True)

        self.add_experiment_variable("size", ["5000"])
        self.set_required_variables(
            n_resources="{n_ranks}",
            process_problem_size="{size}/{n_ranks}",
            total_problem_size="{size}",
        )

    def compute_package_section(self):
        spec = f"genesis{self.determine_version()} precision=mixed "
        if self.spec.variants["backend"][0] == "gpu":
            spec += " +gpu cuda_arch=90 "

        self.add_package_spec(self.name, [spec])
