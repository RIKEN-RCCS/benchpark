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

    def cluster_name(self):
        # Machine identification.
        #
        # The RIKEN cloud machines were formerly a single system,
        # riken-cloud, distinguished by its `cluster` variant; each is now
        # its own system (riken-dgx, riken-gh200, riken-genoa,
        # riken-fx700). Both forms are accepted, since riken-cloud remains
        # selectable.
        #
        # Without this, none of the branches below is reached for a
        # per-machine system, processes_per_node is never set, and n_ranks
        # resolves to None. The failure is reported in the allocation
        # modifier rather than here:
        #
        #     modifiers/allocation/modifier.py:300, in determine_allocation
        #       v.n_ranks_per_node = v.n_ranks // v.n_nodes
        #     TypeError: unsupported operand type(s) for //: 'NoneType' and 'int'
        name = self.system_spec.name
        if name == "riken-cloud":
            return self.system_spec.variants["cluster"][0]
        if name.startswith("riken-"):
            return name[len("riken-") :]
        return name

    def compute_applications_section(self):
        self.add_experiment_variable("n_nodes", ["1"], True)
        cluster = self.cluster_name()

        if cluster == "fugaku":
            self.add_experiment_variable("processes_per_node", ["4"], True)
            self.add_experiment_variable("preprocess", "", False)
            if self.spec.satisfies("+openmp"):
                self.add_experiment_variable("omp_num_threads", ["12"], True)

        else:
            match cluster:
                case "gh200":
                    self.add_experiment_variable("processes_per_node", ["1"], True)
                    # No module juggling, for the reason the dgx branch
                    # below already has none: `module purge` runs in the
                    # same shell as the run steps, so it replaces the
                    # environment spack set up, and the binary then meets
                    # an MPI it was not built against:
                    #
                    #     .../bin/salmon: symbol lookup error
                    #     Exit code: 127
                    #
                    # salmon is built here against the MPI the system
                    # provides to spack; loading nvhpc-hpcx on top of that
                    # is what breaks it.
                    self.add_experiment_variable("preprocess", "", False)

                case "dgx":
                    self.add_experiment_variable("processes_per_node", ["1"], True)
                    # self.add_experiment_variable("preprocess", "module purge && module load system/ng-dgx && module load nvhpc-hpcx-cuda13/26.3 && ", False)
                    self.add_experiment_variable("preprocess", "", False)

                case "fx700":
                    self.add_experiment_variable("processes_per_node", ["4"], True)
                    self.add_experiment_variable(
                        "preprocess",
                        "module purge && module load system/fx700 && module load FJSVstclanga/1.0.30.01 && ",
                        False,
                    )
                    if self.spec.satisfies("+openmp"):
                        self.add_experiment_variable("omp_num_threads", ["12"], True)

                case "genoa":
                    self.add_experiment_variable("processes_per_node", ["1"], True)
                    # No modules: genoa runs Ubuntu 24.04 since the 2026-10
                    # maintenance and has no `module` command, so the old
                    # `module purge && module load ...` stopped the run
                    # before the input was copied. The MPI is the system's,
                    # declared to spack.
                    self.add_experiment_variable("preprocess", "", False)
                    if self.spec.satisfies("+openmp"):
                        self.add_experiment_variable("omp_num_threads", ["48"], True)

        self.add_experiment_variable(
            "n_ranks", "{processes_per_node} * {n_nodes}", True
        )
        self.add_experiment_variable(
            "size", 44051, True
        )  # Defined by rgrid in input files

        self.set_required_variables(
            n_resources="{n_ranks}",
            process_problem_size="{size}/{n_ranks}",
            total_problem_size="{size}",
        )

    def compute_package_section(self):
        self.add_package_spec(self.name, [f"salmon-tddft{self.determine_version()}"])
