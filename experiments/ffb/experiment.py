# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from benchpark.directives import maintainers, variant
from benchpark.error import BenchparkError
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

    # The archives the package declares, by machine and backend, with the
    # compute capability of the machine's GPU for the GPU archive.
    #
    # The versions are named per machine, and the names nest (67.01-cpu,
    # 67.01-cpu-genoa, 67.01-gpu-gh200), so they are requested exactly
    # with `@=`. A bare `@` is a range: `ffb@67.01-cpu` also matches
    # `67.01-cpu-genoa`, which spack then selects, and the fetch fails on a
    # machine where that archive is not present:
    #
    #     Error: FetchError: All fetchers failed for
    #       spack-stage-ffb-67.01-cpu-genoa-...
    #
    # An undeclared version is no better with `@=`: spack concretizes
    # `ffb@=67.01-cpu-gh200` without complaint and fails only at the fetch.
    # Building the name from the machine and backend produced such names
    # for every combination without an archive, so look it up here and
    # stop at `benchpark experiment init` instead. See
    # RIKEN-RCCS/benchpark#7.
    _archives = {
        # Fugaku's archive carries no machine suffix
        # (url ffb-frt_cpu.fugaku.tar.gz).
        ("fugaku", "cpu"): ("cpu", None),
        ("genoa", "cpu"): ("cpu-genoa", None),
        ("gh200", "gpu"): ("gpu-gh200", "90"),
    }

    def _machine(self):
        """The machine this system runs on, as used in _archives.

        riken-cloud names its machine with a `cluster` variant; the
        machines that left it (riken-gh200, riken-genoa, ...) name it in
        the system name. Reading variants['cluster'] on those raises
        KeyError, so accept both forms.
        """
        name = self.system_spec.name
        if name == "riken-cloud":
            cluster = self.system_spec.variants.get("cluster")
            return cluster[0] if cluster else None
        if name.startswith("riken-"):
            return name[len("riken-"):]
        return None

    def compute_package_section(self):
        base_version = self.spec.variants["version"][0]
        # The GPU archive is selected by the experiment's own `backend`
        # variant, as in the genesis experiment, rather than by the system's
        # compiler. The two are not the same choice: riken-gh200's
        # `compiler=cuda` is gcc with CUDA, while the GPU archive compiles
        # with nvfortran-only flags (-Mpreprocess, -acc, -gpu=managed,
        # -cuda) and links nvc++ objects, so it needs compiler=nvhpc.
        backend = self.spec.variants["backend"][0]
        machine = self._machine()

        archive = self._archives.get((machine, backend))
        if archive is None:
            available = ", ".join(
                f"{m} backend={b}" for m, b in sorted(self._archives)
            )
            raise BenchparkError(
                f"ffb has no {backend} archive for system "
                f"{self.system_spec.name}"
                + (f" (machine {machine})" if machine else "")
                + f"; archives exist for: {available}"
            )
        suffix, cuda_arch = archive
        spec_str = f"ffb@={base_version}-{suffix}"

        if cuda_arch:
            # The GPU archive compiles with `-gpu=managed` and defines
            # -Dgpudirect, so it hands device pointers to MPI and needs a
            # CUDA-aware MPI.
            #
            # The system provides openmpi as a non-buildable external (the
            # HPC-X build in the NVIDIA HPC SDK). An external carries no
            # compiler and no dependencies, so `^openmpi %nvhpc` or
            # `^ucx+cuda` cannot be satisfied:
            #
            #     Cannot build openmpi, since it is configured
            #     `buildable:false` and no externals satisfy the request
            spec_str += f" %nvhpc ^openmpi+cuda cuda_arch={cuda_arch}"

        self.add_package_spec(self.name, [spec_str])
