# Copyright 2026
# SPDX-License-Identifier: Apache-2.0

from benchpark.directives import maintainers, variant
from benchpark.experiment import Experiment
from benchpark.programming_model import ProgrammingModel, ProgrammingModelType


class Mvmc(
    Experiment,
    ProgrammingModel(ProgrammingModelType.Mpionly),
):
    """mVMC FermionHubbard benchmark."""

    variant(
        "workload",
        default="fermion_hubbard",
        description="Which Ramble workload to execute.",
    )

    variant(
        "version",
        default="1.3.0",
        values=("1.2.0", "1.3.0"),
        description="Which mVMC version to use.",
    )

    maintainers("otsukay")

    def compute_applications_section(self):
        # The Spack recipe used for mVMC does not define an "openmp" variant,
        # so the Benchpark programming model is kept as MPI-only. Runtime
        # threading is controlled by OMP_NUM_THREADS in the Ramble application.
        if (
            self.system_spec.satisfies("riken-cloud cluster=gh200")
            or self.system_spec.satisfies("riken-rikyu")
        ):
            # CPU-only smoke test; Rikyu permits 32 CPUs per allocated GPU.
            ranks_per_node = 2 if self.system_spec.satisfies("riken-rikyu") else 6
            self.add_experiment_variable("n_nodes", 1, True)
            self.add_experiment_variable("n_ranks", ranks_per_node, True)
            if self.system_spec.satisfies("riken-rikyu"):
                # Reserve one GPU to satisfy allocation policy; computation is CPU-only.
                self.add_experiment_variable("n_gpus", 1, False)
            self.add_experiment_variable(
                "extra_batch_opts",
                "--nodes={n_nodes} "
                f"--ntasks-per-node={ranks_per_node} "
                "--cpus-per-task={n_threads_per_proc}",
                False,
            )
            self.set_environment_variable("OMP_PLACES", "cores")
            self.set_environment_variable("OMP_PROC_BIND", "close")
        else:
            # Run condition corresponding to the supplied Fugaku script:
            # 12 nodes x 4 ranks/node x 12 threads/rank.
            self.add_experiment_variable("n_nodes", 12, True)
            self.add_experiment_variable("n_ranks", 48, True)

        self.add_experiment_variable(
            "n_threads_per_proc", ["12"], named=True, matrixed=True
        )

        # Parameters for the FermionHubbard input file written as Hubbard.def.
        self.add_experiment_variable("W", 18, True)
        self.add_experiment_variable("L", 18, True)
        self.add_experiment_variable("Wsub", 1, False)
        self.add_experiment_variable("Lsub", 1, False)
        self.add_experiment_variable("model", "FermionHubbard", False)
        self.add_experiment_variable("lattice", "Tetragonal", False)
        self.add_experiment_variable("t", "1.0", False)
        self.add_experiment_variable("U", "8.0", False)
        self.add_experiment_variable("ncond", 100, False)
        self.add_experiment_variable("nsr_opt_itr_step", 1, False)
        self.add_experiment_variable("nvmc_sample", 4000, False)
        self.add_experiment_variable("two_sz", 0, False)

        # Fixed-size benchmark metadata.  Use numeric strings here instead of
        # strings such as "18x18" to avoid expression-parsing warnings.
        self.set_required_variables(
            n_resources="{n_ranks}",
            process_problem_size="{total_problem_size} / {n_ranks}",
            total_problem_size="324",
        )

    def compute_package_section(self):
        self.add_package_spec(self.name, [f"mvmc{self.determine_version()}"])
