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
        values=(
            "Si-1-1-1",
            # "Si-2-2-2",
            # "Si-3-3-3",
            # "Si-4-4-4",
        ),
        multi=True,
        description="salmon-tddft",
    )

    variant(
        "version",
        default="2.2.2",
        description="app version",
    )

    variant(
        "openacc",
        default=False,
        description="Build SALMON with OpenACC",
    )

    def compute_applications_section(self):
        self.add_experiment_variable("n_nodes", ["1"], True)
        self.add_experiment_variable("processes_per_node", ["1"], True)

        input_urls = {
            "riken-fugaku": "file:///vol0500/share/ra250029/CX_input/SALMON/SALMON.tar.gz",
            "riken-rikyu": "file:///data1/rkp00015/CX_input/SALMON/SALMON.tar.gz",
            "riken-gh200": "file:///lvs0/dne1/rccs-nghpcadu/CX_input/SALMON/SALMON.tar.gz",
            "riken-dgx": "file:///lvs0/dne1/rccs-nghpcadu/CX_input/SALMON/SALMON.tar.gz",
            "riken-fx700": "file:///lvs0/dne1/rccs-nghpcadu/CX_input/SALMON/SALMON.tar.gz",
            "riken-genoa": "file:///lvs0/dne1/rccs-nghpcadu/CX_input/SALMON/SALMON.tar.gz",
        }
        self.add_experiment_variable("salmon_input_url", input_urls[self.system_spec.name], False)
        if self.system_spec.name == 'riken-fugaku':
            # Fujitsu MPI forwards stdin using an MPI option before the executable.
            self.add_experiment_variable("salmon_gs_stdin_option", "-stdin {input_data_gs}", False)
            self.add_experiment_variable("salmon_rt_stdin_option", "-stdin {input_data_rt}", False)
            self.add_experiment_variable("salmon_gs_stdin_redirect", "", False)
            self.add_experiment_variable("salmon_rt_stdin_redirect", "", False)
            self.add_experiment_variable("processes_per_node", ["4"], True)
            self.add_experiment_variable("preprocess", "", False)
            threads = 12 if self.spec.satisfies("+openmp") else 1
            self.add_experiment_variable("n_threads_per_proc", str(threads), False)
            # fjomplib fast mode overrides OMP_DYNAMIC. Allow its software-barrier
            # fallback without turning a completed calculation into exit status 4.
            self.add_experiment_variable(
                "pre_exec_cmds",
                "export FLIB_FASTOMP=FALSE FLIB_CNTL_BARRIER_ERR=FALSE "
                "OMP_NUM_THREADS={n_threads_per_proc} OMP_DYNAMIC=FALSE "
                "OMP_PLACES=cores OMP_PROC_BIND=close OPENBLAS_NUM_THREADS=1",
                False,
            )

        elif self.system_spec.name == 'riken-rikyu':
            self.add_experiment_variable("processes_per_node", ["1"], True)
            if self.spec.satisfies("+openacc"):
                self.add_experiment_variable("n_gpus", "1", False)
            nvhpc_version = self.system_spec.variants["nvhpc"][0]
            self.add_experiment_variable("preprocess", f"module load nvhpc-hpcx/{nvhpc_version} && ", False)

        elif self.system_spec.name in ('riken-gh200', 'riken-dgx', 'riken-fx700', 'riken-genoa'):
            match self.system_spec.name:
                case 'riken-gh200':
                    self.add_experiment_variable("processes_per_node", ["1"], True)
                    if self.spec.satisfies("+openacc"):
                        self.add_experiment_variable("n_gpus", "1", False)
                    self.add_experiment_variable("preprocess", "", False)

                case 'riken-dgx':
                    self.add_experiment_variable("processes_per_node", ["1"], True)
                    if self.spec.satisfies("+openacc"):
                        self.add_experiment_variable("n_gpus", "1", False)
                    if self.system_spec.variants["compiler"][0] == "nvhpc":
                        nvhpc_version = self.system_spec.variants["nvhpc"][0]
                        nvhpc_cuda_version = {
                            "26.9": "13.3", "26.5": "13.2", "26.3": "13.1",
                            "25.9": "13.0", "25.7": "12.9", "24.3": "12.3",
                        }[nvhpc_version]
                        mpi_prefix = (
                            f"/opt/nvidia/hpc_sdk/Linux_aarch64/{nvhpc_version}"
                            f"/comm_libs/{nvhpc_cuda_version}/hpcx/latest/ompi4"
                        )
                        pre_exec = self.system_spec.system.system_specific_variables()["pre_exec_cmds"]
                        self.add_experiment_variable(
                            "pre_exec_cmds",
                            pre_exec + "; unset PMIX_INSTALL_PREFIX PMIX_PREFIX; "
                            f"export OPAL_PREFIX={mpi_prefix}; "
                            f"export PATH={mpi_prefix}/bin:$PATH; "
                            f"export LD_LIBRARY_PATH={mpi_prefix}/lib:$LD_LIBRARY_PATH",
                            False,
                        )
                    self.add_experiment_variable("preprocess", "", False)

                case 'riken-fx700':
                    self.add_experiment_variable("processes_per_node", ["4"], True)
                    # Fujitsu fast mode overrides OMP_DYNAMIC and reports exit 4.
                    # Use the same software-barrier fallback controls as Fugaku.
                    self.add_experiment_variable(
                        "pre_exec_cmds",
                        "module load FJSVstclanga/1.0.30.01; "
                        "export SLURM_MPI_TYPE=pmix FLIB_FASTOMP=FALSE FLIB_CNTL_BARRIER_ERR=FALSE "
                        "OMP_NUM_THREADS={n_threads_per_proc} OMP_DYNAMIC=FALSE "
                        "OMP_PLACES=cores OMP_PROC_BIND=close OPENBLAS_NUM_THREADS=1",
                        False,
                    )
                    self.add_experiment_variable("preprocess", "", False)
                    threads = 12 if self.spec.satisfies("+openmp") else 1
                    self.add_experiment_variable("n_threads_per_proc", str(threads), False)

                case 'riken-genoa':
                    # Genoa has 96 physical cores (192 hardware threads).
                    # For the Si grid, 64 ranks give a valid 4x4x4 split;
                    # ceil-based splits at 48/96 ranks leave blocks below stencil width.
                    ranks, threads = (8, 12) if self.spec.satisfies("+openmp") else (64, 1)
                    self.add_experiment_variable("processes_per_node", [str(ranks)], True)
                    self.add_experiment_variable("n_threads_per_proc", str(threads), False)
                    self.add_experiment_variable(
                        "extra_cmd_opts",
                        "--cpu-bind=cores --hint=nomultithread",
                        False,
                    )
                    self.add_experiment_variable(
                        "pre_exec_cmds",
                        "export SLURM_MPI_TYPE=pmix OMP_NUM_THREADS={n_threads_per_proc} OMP_DYNAMIC=FALSE "
                        "OMP_PLACES=cores OMP_PROC_BIND=close OPENBLAS_NUM_THREADS=1",
                        False,
                    )
                    self.add_experiment_variable("preprocess", "", False)

        self.add_experiment_variable("n_ranks", "{processes_per_node} * {n_nodes}", True)

        self.set_required_variables(
            n_resources="{n_ranks}",
            process_problem_size="{size}/{n_ranks}",
            total_problem_size="{size}"
        )

    def compute_package_section(self):
        openacc = " +openacc" if self.spec.satisfies("+openacc") else ""
        fx700 = (
            " +fx700"
            if self.system_spec.name == "riken-fx700"
            and self.system_spec.variants["compiler"][0] == "fj"
            else ""
        )
        self.add_package_spec(
            self.name, [f"salmon-tddft{self.determine_version()}{openacc}{fx700}"]
        )
