# Copyright 2026
# SPDX-License-Identifier: Apache-2.0

from benchpark.directives import maintainers, variant
from benchpark.experiment import Experiment
from benchpark.programming_model import ProgrammingModel, ProgrammingModelType


class Mvmc(
    Experiment,
    ProgrammingModel(ProgrammingModelType.Mpionly),
):
    """mVMC FermionHubbard benchmark on Fugaku."""

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
        # Run condition corresponding to the supplied Fugaku script:
        #   12 nodes, 48 MPI processes, 12 OpenMP threads per MPI process.
        #
        # The Spack recipe used for mVMC does not define an "openmp" variant,
        # so the Benchpark programming model is kept as MPI-only. Runtime
        # threading is controlled by OMP_NUM_THREADS in the Ramble application.
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
            process_problem_size="6.75",
            total_problem_size="324",
        )

    def compute_package_section(self):
        self.add_package_spec(self.name, [f"mvmc{self.determine_version()}"])
