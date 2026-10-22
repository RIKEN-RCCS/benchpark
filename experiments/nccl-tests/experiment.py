# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from benchpark.directives import maintainers, variant
from benchpark.error import BenchparkError
from benchpark.experiment import Experiment
from benchpark.programming_model import ProgrammingModel, ProgrammingModelType


class NcclTests(
    Experiment,
    ProgrammingModel(
        ProgrammingModelType.Mpionly,
        ProgrammingModelType.Cuda,
    ),
):
    """NCCL Tests (https://github.com/NVIDIA/nccl-tests): the performance and
    correctness of NCCL collectives. The spack package is spack's own
    nccl-tests, the ramble application ramble's own plus the benchmarks it
    does not list (broadcast, gather, reduce, scatter, hypercube).
    """

    variant(
        "workload",
        default="all-reduce",
        values=(
            "all-gather",
            "all-reduce",
            "all-to-all",
            "broadcast",
            "gather",
            "hypercube",
            "reduce",
            "reduce-scatter",
            "scatter",
            "send-recv",
        ),
        multi=True,
        description="workloads to run",
    )

    variant(
        "version",
        default="2.17.6",
        values=("latest", "2.17.6", "2.16.3"),
        description="app version",
    )

    # Shape of the run
    variant("nprocs", default="2", description="Number of MPI ranks")
    variant(
        "nthreads_proc",
        default="1",
        description="Number of threads per rank (-t)",
    )
    variant(
        "ngpus_thread",
        default="1",
        description="Number of GPUs per thread (-g)",
    )

    # nccl-tests command line options. "none" leaves the benchmark's default,
    # except where ramble's application sets one (min_bytes 8, max_bytes 8G,
    # step_factor 2, num_iters 100, warmup_iters 5, result_check 1).
    variant("min_bytes", default="none", description="Smallest message size (-b)")
    variant("max_bytes", default="none", description="Largest message size (-e)")
    variant(
        "step_inc",
        default="none",
        description="Message size increment (-i); excludes step_factor",
    )
    variant(
        "step_factor",
        default="none",
        description="Message size multiplier (-f); excludes step_inc",
    )
    variant("op", default="none", description="Reduction operation sum/prod/min/max/avg/all (-o)")
    variant("datatype", default="none", description="Data type <nccltype>/all (-d)")
    variant("root", default="none", description="Root rank <rank>/all (-r)")
    variant("num_iters", default="none", description="Iterations (-n)")
    variant("warmup_iters", default="none", description="Warmup iterations (-w)")
    variant("agg_iters", default="none", description="Operations aggregated per iteration (-m)")
    variant("run_cycles", default="none", description="Cycles to run and report, 0 = infinite (-N)")
    variant(
        "average",
        default="none",
        description="Which rank's figures to report: 0 rank 0, 1 average, 2 min, 3 max (-a)",
    )
    variant("parallel_init", default="none", description="Initialise NCCL from threads 0/1 (-p)")
    variant("result_check", default="none", description="Iterations whose results are checked (-c)")
    variant("blocking", default="none", description="Blocking collectives 0/1 (-z)")
    variant("cudagraph", default="none", description="Replays of the captured CUDA graph (-G)")
    variant("report_cputime", default="none", description="Report CPU time instead of latency 0/1 (-C)")
    variant("local_register", default="none", description="Buffer registration 0 none, 1 local, 2 symmetric (-R)")
    variant("report_timestamps", default="none", description="Timestamp each report line 0/1 (-S)")
    variant("output_file", default="none", description="JSON output file (-J)")
    variant("timeout", default="none", description="Seconds after which a test is abandoned (-T)")

    maintainers("nhanford")

    # (variant, ramble variable it sets)
    ramble_variables = [
        ("min_bytes", "begin_message_size"),
        ("max_bytes", "end_message_size"),
        ("step_factor", "message_size_factor"),
        ("ngpus_thread", "num_gpus_per_task"),
        ("warmup_iters", "warmup_iters"),
        ("num_iters", "num_iters"),
        ("result_check", "result_check"),
    ]

    # (variant, flag) for the options ramble's application does not know
    extra_options = [
        ("nthreads_proc", "-t"),
        ("op", "-o"),
        ("datatype", "-d"),
        ("root", "-r"),
        ("agg_iters", "-m"),
        ("run_cycles", "-N"),
        ("average", "-a"),
        ("parallel_init", "-p"),
        ("blocking", "-z"),
        ("cudagraph", "-G"),
        ("report_cputime", "-C"),
        ("local_register", "-R"),
        ("report_timestamps", "-S"),
        ("output_file", "-J"),
        ("timeout", "-T"),
    ]

    def variant_value(self, name):
        return str(self.spec.variants[name][0])

    def compute_applications_section(self):
        if not self.spec.satisfies("+cuda"):
            raise BenchparkError("nccl-tests needs +cuda")

        n_ranks = int(self.variant_value("nprocs"))
        n_threads = int(self.variant_value("nthreads_proc"))
        n_gpus_thread = int(self.variant_value("ngpus_thread"))
        if n_ranks < 1 or n_threads < 1 or n_gpus_thread < 1:
            raise BenchparkError("nprocs, nthreads_proc and ngpus_thread must be positive")
        n_gpus = n_ranks * n_threads * n_gpus_thread

        sys = self.system_spec.system
        gpus_per_node = getattr(sys, "sys_gpus_per_node", None)
        if gpus_per_node and n_threads * n_gpus_thread > int(gpus_per_node):
            raise BenchparkError(
                f"one rank wants {n_threads * n_gpus_thread} GPUs, the node has {gpus_per_node}"
            )

        for name, ramble_var in self.ramble_variables:
            value = self.variant_value(name)
            if name == "ngpus_thread" or value != "none":
                self.add_experiment_variable(ramble_var, value, False)

        step_inc = self.variant_value("step_inc")
        if step_inc != "none" and self.variant_value("step_factor") != "none":
            raise BenchparkError("step_inc (-i) and step_factor (-f) exclude each other")

        # ramble's default arguments, with -i in place of -f when asked
        args = [
            "-b {begin_message_size}",
            "-e {end_message_size}",
            f"-i {step_inc}" if step_inc != "none" else "-f {message_size_factor}",
            "-g {num_gpus_per_task}",
            "-w {warmup_iters}",
            "--iters {num_iters}",
            "-c {result_check}",
        ]
        for name, flag in self.extra_options:
            value = self.variant_value(name)
            if name == "nthreads_proc":
                if n_threads > 1:
                    args.append(f"{flag} {value}")
            elif value != "none":
                args.append(f"{flag} {value}")
        self.add_experiment_variable("additional_args", " ".join(args), False)

        self.add_experiment_variable("n_ranks", n_ranks, True)
        self.add_experiment_variable("n_gpus", n_gpus, True)
        self.set_required_variables(
            n_resources="{n_gpus}",
            process_problem_size="{end_message_size}",
            total_problem_size="{end_message_size}",
        )

    def compute_package_section(self):
        pkg_spec = f"nccl-tests{self.determine_version()}"
        pkg_spec += "+mpi" if self.spec.satisfies("+mpi") else "~mpi"
        self.add_package_spec(self.name, [pkg_spec])
