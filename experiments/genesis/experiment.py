# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from benchpark.cuda import CudaExperiment
from benchpark.directives import maintainers, variant
from benchpark.experiment import Experiment
from benchpark.mpi import MpiOnlyExperiment
from benchpark.openmp import OpenMPExperiment

class Genesis(Experiment, MpiOnlyExperiment, OpenMPExperiment, CudaExperiment,):

    variant(
        "workload",
        default="DHFR",
        # Lyzozyme : < 4 GPU would be better, 
        # DHFR : < 4 GPU would be better, 
        # Apoa1 100K atoms :  1-16 GPUs OK, 
        # UUN 200K atoms : 1-32/64 GPUs OK
        # CryoEM (GPU not work)
        values=("Lysozyme", "DHFR", "ApoA1", "UUN", "cryoEM"),
        description="genesis",
    )

    variant(
        "backend",
        default="cpu",
        values=("cpu","gpu"),
        description="genesis backend (cpu or gpu)"
    )

    variant(
        "precision",
        default="mixed",
        values=("double","mixed","single"),
        description="Floating point precision"
    )

    variant(
        "version",
        default="2.1.6",
        values=("2.1.6", "main"),
        description="app version",
    )

    maintainers("jdomke", "SBA0486", "chig")

    def compute_applications_section(self):
        #        if self.spec.satisfies("exec_mode=test"):
        #            self.add_experiment_variable("processes_per_node", ["8"])
        #        # Must be exec_mode=perf
        #        else:
        #            self.add_experiment_variable("processes_per_node", ["8"])

        n_resources = 8
        self.add_experiment_variable("n_resources", [str(n_resources)])
        self.add_experiment_variable("n_ranks", "{n_resources}")

        if self.spec.satisfies("+openmp"):
            self.add_experiment_variable("n_nodes", "1", True)
            self.add_experiment_variable(
                    "n_threads_per_proc", 
                    ["{sys_cores_per_node} // {n_ranks}"])
        elif self.spec.satisfies("+cuda"):
            self.add_experiment_variable("n_nodes", "1", True)
            #self.add_experiment_variable("n_gpus", "1")


        self.set_required_variables(
            process_problem_size="{size}/{n_ranks}",
            total_problem_size="{size}",
        )

    def compute_package_section(self):
        precision = self.spec.variants["precision"][0]
        spec = f"genesis{self.determine_version()} precision={precision} "
        if self.spec.variants["backend"][0] == "gpu":
            spec += " +gpu "

        self.add_package_spec(self.name, [spec])
