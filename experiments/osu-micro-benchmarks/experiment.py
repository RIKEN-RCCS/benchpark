# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from benchpark.directives import maintainers, variant
from benchpark.error import BenchparkError
from benchpark.experiment import Experiment
from benchpark.programming_model import ProgrammingModel, ProgrammingModelType
from benchpark.scaling import Scaling, ScalingMode


class OsuMicroBenchmarks(
    Experiment,
    ProgrammingModel(
        ProgrammingModelType.Mpionly,
        ProgrammingModelType.Cuda,
        ProgrammingModelType.Rocm,
    ),
    Scaling(ScalingMode.Strong, ScalingMode.Throughput),
):

    two_rank_workloads = [
        "osu_bibw",
        "osu_bw",
        "osu_latency",
        "osu_get_acc_latency",
        "osu_get_bw",
        "osu_get_latency",
        "osu_put_bibw",
        "osu_put_bw",
        "osu_put_latency",
    ]

    scalable_workloads = [
        "osu_latency_mp",
        "osu_latency_mt",
        "osu_mbw_mr",
        "osu_multi_lat",
        "osu_allgather",
        "osu_allreduce_persistent",
        "osu_alltoallw",
        "osu_bcast_persistent",
        "osu_iallgather",
        "osu_ialltoallw",
        "osu_ineighbor_allgather",
        "osu_ireduce",
        "osu_neighbor_allgatherv",
        "osu_reduce_persistent",
        "osu_scatterv",
        "osu_allgather_persistent",
        "osu_alltoall",
        "osu_alltoallw_persistent",
        "osu_gather",
        "osu_iallgatherv",
        "osu_ibarrier",
        "osu_ineighbor_allgatherv",
        "osu_ireduce_scatter",
        "osu_neighbor_alltoall",
        "osu_reduce_scatter",
        "osu_scatterv_persistent",
        "osu_allgatherv",
        "osu_alltoall_persistent",
        "osu_barrier",
        "osu_gather_persistent",
        "osu_iallreduce",
        "osu_ibcast",
        "osu_ineighbor_alltoall",
        "osu_iscatter",
        "osu_neighbor_alltoallv",
        "osu_reduce_scatter_persistent",
        "osu_allgatherv_persistent",
        "osu_alltoallv",
        "osu_barrier_persistent",
        "osu_gatherv",
        "osu_ialltoall",
        "osu_igather",
        "osu_ineighbor_alltoallv",
        "osu_iscatterv",
        "osu_neighbor_alltoallw",
        "osu_scatter",
        "osu_allreduce",
        "osu_alltoallv_persistent",
        "osu_bcast",
        "osu_gatherv_persistent",
        "osu_ialltoallv",
        "osu_igatherv",
        "osu_ineighbor_alltoallw",
        "osu_neighbor_allgather",
        "osu_reduce",
        "osu_scatter_persistent",
        "osu_cas_latency",
        "osu_fop_latency",
        "osu_hello",
        "osu_init",
    ]

    # Benchmarks OMB 7.5 builds that the two lists above do not name (added
    # with the RIKEN-RCCS work). The point-to-point ones run on two ranks like
    # two_rank_workloads, the rest fill the nodes like scalable_workloads. The
    # osu_xccl_* benchmarks need +xccl, the osu_oshm_* ones an MPI that ships
    # an OpenSHMEM compiler (the package builds them with its oshcc).
    riken_two_rank_workloads = [
        "osu_acc_latency",
        "osu_latency_persistent",
        "osu_bw_persistent",
        "osu_bibw_persistent",
        "osu_xccl_latency",
        "osu_xccl_bw",
        "osu_xccl_bibw",
    ]

    xccl_collective_workloads = [
        "osu_xccl_allgather",
        "osu_xccl_allreduce",
        "osu_xccl_alltoall",
        "osu_xccl_bcast",
        "osu_xccl_reduce",
        "osu_xccl_reduce_scatter",
    ]

    oshm_workloads = [
        "osu_oshm_atomics",
        "osu_oshm_barrier",
        "osu_oshm_broadcast",
        "osu_oshm_collect",
        "osu_oshm_fcollect",
        "osu_oshm_get",
        "osu_oshm_get_bw",
        "osu_oshm_get_mr_nb",
        "osu_oshm_get_nb",
        "osu_oshm_get_nb_bw",
        "osu_oshm_get_overlap",
        "osu_oshm_put",
        "osu_oshm_put_bw",
        "osu_oshm_put_mr",
        "osu_oshm_put_mr_nb",
        "osu_oshm_put_nb",
        "osu_oshm_put_nb_bw",
        "osu_oshm_put_overlap",
        "osu_oshm_reduce",
    ]

    riken_scalable_workloads = (
        ["osu_bw_fan_in", "osu_bw_fan_out"] + xccl_collective_workloads + oshm_workloads
    )

    # The point-to-point benchmarks whose buffer arguments distinguish managed
    # memory on the device (MD) from managed memory on the host (MH); every
    # other benchmark takes a plain M.
    pt2pt_workloads = [
        "osu_bibw",
        "osu_bw",
        "osu_latency",
        "osu_latency_mp",
        "osu_latency_mt",
        "osu_mbw_mr",
        "osu_multi_lat",
        "osu_latency_persistent",
        "osu_bw_persistent",
        "osu_bibw_persistent",
    ]

    variant(
        "workload",
        default="osu_latency",
        values=two_rank_workloads
        + scalable_workloads
        + riken_two_rank_workloads
        + riken_scalable_workloads,
        multi=True,
        description="workloads available",
    )

    variant(
        "version",
        default="7.5",
        values=("latest", "7.5", "7.5.1", "7.5.2"),
        description="app version",
    )

    # Build options (RIKEN-RCCS additions)
    variant(
        "xccl",
        default=False,
        description="Build the NCCL/RCCL benchmarks (osu_xccl_*); needs +cuda or +rocm",
    )
    variant(
        "papi",
        default=False,
        description="Build with PAPI and record the counters in papi_events (-P)",
    )
    variant(
        "graphing",
        default=False,
        description="Build with graphing support and draw a graph of each run (-G)",
    )

    # Run options (RIKEN-RCCS additions). "none" leaves OMB's own default.
    variant(
        "managed",
        default=False,
        description="Allocate CUDA buffers as managed memory (-d managed instead of -d cuda)",
    )
    variant(
        "buffers",
        default="none",
        values=(
            "none",
            "host_to_host",
            "gpu_to_gpu",
            "host_to_gpu",
            "gpu_to_host",
            "managed_to_managed",
            "host_buffer",
            "gpu_buffer",
            "managed_buffer",
        ),
        description="Where the buffers live, as OMB's trailing SRC DST arguments: "
        "<src>_to_<dst> names the two ends of a point-to-point or one-sided benchmark, "
        "<kind>_buffer the (same) kind for both arguments of a collective; "
        "gpu and managed need +cuda or +rocm",
    )
    variant(
        "min_message_size",
        default="none",
        description="Smallest message size in bytes (-m min:max); needs max_message_size",
    )
    variant(
        "max_message_size",
        default="none",
        description="Largest message size in bytes (-m)",
    )
    variant(
        "iterations",
        default="none",
        description="Iterations per message size (-i)",
    )
    variant(
        "warmup_iterations",
        default="none",
        description="Warmup iterations per message size (-x)",
    )
    variant(
        "tail_statistics",
        default=False,
        description="Report P50/P90/P99 tail latency or bandwidth as well (-z)",
    )
    variant(
        "papi_events",
        default="PAPI_TOT_INS:PAPI_TOT_CYC:PAPI_L1_DCM:PAPI_L1_ICM:PAPI_L2_DCM",
        description="PAPI events to record, colon-separated (+papi)",
    )
    variant(
        "papi_output",
        default="papi.out",
        description="File the PAPI counters are written to (+papi)",
    )
    variant(
        "graph_type",
        default="png",
        description="Graph format for -G (+graphing)",
    )

    maintainers("nhanford")

    def selected_workloads(self):
        return [w for w in self.spec.variants["workload"]]

    def buffer_args(self, workloads):
        """OMB's trailing buffer arguments for the `buffers` variant."""
        choice = self.spec.variants["buffers"][0]
        if choice == "none":
            return []

        accel = self.spec.satisfies("+cuda") or self.spec.satisfies("+rocm")
        if ("gpu" in choice or "managed" in choice) and not accel:
            raise BenchparkError(f"buffers={choice} needs +cuda or +rocm")
        if "managed" in choice and not self.spec.satisfies("+managed"):
            raise BenchparkError(f"buffers={choice} needs +managed")

        pt2pt = [w in self.pt2pt_workloads for w in workloads]
        if "managed" in choice and any(pt2pt) and not all(pt2pt):
            raise BenchparkError(
                "Managed buffers are spelled MD for point-to-point benchmarks and M "
                "for the others; keep the two kinds in separate experiments"
            )
        managed = "MD" if all(pt2pt) else "M"
        letter = {"host": "H", "gpu": "D", "managed": managed}

        # OMB 7.5.x takes SRC DST for the collectives as well (a single
        # letter is a usage error), so <kind>_buffer gives the kind twice.
        if choice.endswith("_buffer"):
            kind = letter[choice[: -len("_buffer")]]
            return [kind, kind]
        src, dst = choice.split("_to_")
        return [letter[src], letter[dst]]

    def compute_applications_section(self):

        if self.spec.satisfies("exec_mode=test"):
            num_nodes = {"n_nodes": 1, "n_ranks": 2}
            for pk, pv in num_nodes.items():
                self.add_experiment_variable(pk, pv, True)

        workloads = self.selected_workloads()

        # The arguments every workload of the experiment runs with. Options
        # first, the buffer placement last: OMB parses its options in POSIX
        # order and stops at the first non-option argument.
        args = []
        if self.spec.satisfies("+rocm"):
            args.append("-d rocm")
        if self.spec.satisfies("+cuda"):
            args.append("-d managed" if self.spec.satisfies("+managed") else "-d cuda")

        # Always with the colon. OMB 7.5.x reads a lone number as the
        # minimum, whatever its help says, and a minimum above the default
        # maximum leaves the benchmark with no sizes to run (osu_bw dies
        # with a segmentation fault); ":MAX" keeps the benchmark's own
        # minimum. The same holds for the collectives.
        min_size = self.spec.variants["min_message_size"][0]
        max_size = self.spec.variants["max_message_size"][0]
        if max_size != "none":
            args.append(f"-m {'' if min_size == 'none' else min_size}:{max_size}")
        elif min_size != "none":
            raise BenchparkError("min_message_size needs max_message_size")
        if self.spec.variants["iterations"][0] != "none":
            args.append(f"-i {self.spec.variants['iterations'][0]}")
        if self.spec.variants["warmup_iterations"][0] != "none":
            args.append(f"-x {self.spec.variants['warmup_iterations'][0]}")
        if self.spec.satisfies("+papi"):
            events = str(self.spec.variants["papi_events"][0]).replace(":", ",")
            args.append(f"-P {events}:{self.spec.variants['papi_output'][0]}")
        if self.spec.satisfies("+graphing"):
            args.append(f"-G {self.spec.variants['graph_type'][0]}")
        if self.spec.satisfies("+tail_statistics"):
            args.append("-z")
        args.extend(self.buffer_args(workloads))

        if args:
            self.add_experiment_variable("additional_args", " " + " ".join(args), False)

        use_gpus = self.spec.satisfies("+cuda") or self.spec.satisfies("+rocm")
        resource_var = "n_gpus" if use_gpus else "n_ranks"
        two_rank = self.two_rank_workloads + self.riken_two_rank_workloads
        scalable = self.scalable_workloads + self.riken_scalable_workloads
        # self.add_experiment_variable("n_nodes", 2 , True)
        if any(self.spec.satisfies(f"workload={wl}") for wl in two_rank):
            if any(self.spec.satisfies(f"workload={wl}") for wl in scalable):
                raise BenchparkError(
                    "This experiment must contain eithor only 2-rank workloads or only scalable workloads."
                )
            # Test the intra-node case and the inter-node case. Ignore user-set scaling params.
            self.add_experiment_variable(resource_var, [2, 2], True)
            self.add_experiment_variable("n_nodes", [1, 2], True)
            self.add_experiment_variable("scaling-iterations", 1, True)
        else:
            sys = self.system_spec.system
            # "Fill" the nodes with ranks, and scale according to user parameters.
            resources_per_node = (
                sys.sys_gpus_per_node if use_gpus else sys.sys_cores_per_node
            )
            self.add_experiment_variable(resource_var, resources_per_node, True)
            self.add_experiment_variable("n_nodes", 1, True)
        self.register_scaling_config(
            {
                ScalingMode.Strong: {
                    "n_nodes": lambda var, itr, dim, scaling_factor: var.val(dim)
                    * scaling_factor,
                    resource_var: lambda var, itr, dim, scaling_factor: var.val(dim)
                    * scaling_factor,
                    "process_problem_size": "",
                    "total_problem_size": "",
                },
                ScalingMode.Throughput: {
                    "n_nodes": None,
                },
            }
        )

        n_resources = "{" + resource_var + "}"
        self.set_required_variables(
            n_resources=n_resources, process_problem_size="", total_problem_size=""
        )

    def compute_package_section(self):
        pkg_spec = f"osu-micro-benchmarks{self.determine_version()}"

        accel = self.spec.satisfies("+cuda") or self.spec.satisfies("+rocm")
        if self.spec.satisfies("+xccl"):
            if not accel:
                raise BenchparkError("+xccl needs +cuda or +rocm")
            pkg_spec += "+xccl"
        elif accel:
            # spack's package turns xccl on with +cuda/+rocm by default, and
            # that pulls NCCL/RCCL into the build. Only +xccl asks for it here.
            pkg_spec += "~xccl"
        if self.spec.satisfies("+papi"):
            pkg_spec += "+papi"
        if self.spec.satisfies("+graphing"):
            pkg_spec += "+graphing"
        if any(w in self.oshm_workloads for w in self.selected_workloads()):
            pkg_spec += "+openshmem"

        self.add_package_spec(self.name, [pkg_spec])
