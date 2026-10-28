# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from benchpark.directives import maintainers, variant
from benchpark.experiment import Experiment
from benchpark.programming_model import ProgrammingModel, ProgrammingModelType


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

    variant(
        "backend",
        default="cpu",
        values=("cpu", "gpu"),
        description="ffb backend (cpu or gpu)",
    )

    maintainers("ando")

    def compute_applications_section(self):
        has_cuda = self.spec.satisfies("backend=gpu")

        # Do not set extra_batch_opts here. The allocation modifier already
        # writes the node count from n_nodes in each scheduler's own syntax
        # (Slurm/Flux -N, PJM -L node=, PBS select=, LSF -nnodes), and `-N`
        # is not a node request everywhere: PJM and PBS take it as the job
        # name, and pjsub rejects the script:
        #
        #     ERR line= 7 .../execute_experiment
        #     ==> Error: Command exited with status 1: pjsub ...
        #
        # Assigning extra_batch_opts also replaces the value the system
        # definition sets, such as the LLIO cache option every riken-fugaku
        # job needs, group_list on jcahpc-miyabi-g, or the account and
        # constraint on other Slurm machines. See RIKEN-RCCS/benchpark#12.

        if has_cuda:  # GPU
            self.add_experiment_variable("n_nodes", 4, True)
            self.add_experiment_variable("processes_per_node", 1)
            self.add_experiment_variable("n_ranks", "{processes_per_node} * {n_nodes}")
            self.add_experiment_variable("size", 31255875, True)
        else:  # CPU
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
        base_version = self.spec.variants["version"][0]
        # Machine identification.
        #
        # riken-cloud distinguished its machines with a `cluster` variant.
        # Since each machine became its own system (riken-dgx, riken-gh200,
        # riken-genoa, riken-fx700), reading variants['cluster'] raises:
        #
        #     benchpark experiment init ... -> KeyError: 'cluster'
        #
        # Accept both forms; a system with neither retains the empty suffix.
        name = self.system_spec.name
        if "cluster" in self.system_spec.variants:
            ret = self.system_spec.variants["cluster"]
            cluster = f"-{ret[0]}" if ret else ""
        elif name.startswith("riken-") and name != "riken-cloud":
            cluster = f"-{name[len('riken-'):]}"
        else:
            cluster = ""

        # The package declares Fugaku's archive without a machine suffix
        # (67.01-cpu, url ffb-frt_cpu.fugaku.tar.gz), alongside
        # 67.01-cpu-genoa and 67.01-gpu-gh200. Appending the machine name
        # for riken-fugaku therefore requests an undeclared version.
        if cluster == "-fugaku":
            cluster = ""

        # The GPU archive is selected by the experiment's own `backend`
        # variant, as in the genesis experiment, rather than by the system's
        # compiler. The two are not the same choice: riken-gh200's
        # `compiler=cuda` is gcc with CUDA, while the GPU archive compiles
        # with nvfortran-only flags (-Mpreprocess, -acc, -gpu=managed,
        # -cuda) and links nvc++ objects, so it needs compiler=nvhpc.
        suffix = "-gpu" if self.spec.satisfies("backend=gpu") else "-cpu"
        # `@=` denotes an exact version; a bare `@` denotes a range.
        # These version names nest, so `ffb@67.01-cpu` also matches
        # `67.01-cpu-genoa`, which spack then selects. The fetch fails on
        # a machine where that archive is not present:
        #
        #     Error: FetchError: All fetchers failed for
        #       spack-stage-ffb-67.01-cpu-genoa-...
        #
        # The same ambiguity reports an undeclared version as
        # "Cannot satisfy 'ffb@67.01-cpu-fugaku' 1(67.01-gpu-gh200)".
        spec_str = f"ffb@={base_version}{suffix}{cluster}"

        if self.spec.satisfies("backend=gpu"):
            # The GPU archive compiles with `-gpu=managed` and defines
            # -Dgpudirect, so it hands device pointers to MPI and needs a
            # CUDA-aware MPI. cuda_arch is the compute capability of the
            # machine's GPU.
            #
            # The system provides openmpi as a non-buildable external (the
            # HPC-X build in the NVIDIA HPC SDK). An external carries no
            # compiler and no dependencies, so `^openmpi %nvhpc` or
            # `^ucx+cuda` cannot be satisfied:
            #
            #     Cannot build openmpi, since it is configured
            #     `buildable:false` and no externals satisfy the request
            cuda_arch = {"riken-gh200": "90", "riken-dgx": "121"}.get(
                self.system_spec.name
            )
            if cuda_arch:
                spec_str += f" %nvhpc ^openmpi+cuda cuda_arch={cuda_arch}"

        self.add_package_spec(self.name, [spec_str])
