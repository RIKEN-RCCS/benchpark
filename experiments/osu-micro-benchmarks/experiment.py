# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from benchpark.directives import maintainers, variant
from benchpark.experiment import Experiment
from benchpark.programming_model import ProgrammingModel, ProgrammingModelType


class OsuMicroBenchmarks(
    Experiment,
    ProgrammingModel(
        ProgrammingModelType.Mpionly,
        ProgrammingModelType.Cuda,
        ProgrammingModelType.Rocm,
    ),
):

    variant(
        "workload",
        default="osu_latency",
        values=(
            "osu_bibw",
            "osu_bw",
            "osu_latency",
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
            "osu_acc_latency",
            "osu_cas_latency",
            "osu_fop_latency",
            "osu_get_acc_latency",
            "osu_get_bw",
            "osu_get_latency",
            "osu_put_bibw",
            "osu_put_bw",
            "osu_put_latency",
            "osu_hello",
            "osu_init",
            "osu_bw_fan_in",
            "osu_bw_fan_out",
            "osu_latency_persistent",
            "osu_bw_persistent",
            "osu_bibw_persistent",
            "osu_oshm_put_bw",
            "osu_oshm_get_nb",
            "osu_oshm_put_mr_nb",
            "osu_oshm_get_nb_bw",
            "osu_oshm_broadcast",
            "osu_oshm_get_overlap",
            "osu_oshm_get_bw",
            "osu_oshm_put_nb_bw",
            "osu_oshm_get_mr_nb",
            "osu_oshm_put_overlap",
            "osu_oshm_reduce",
            "osu_oshm_get",
            "osu_oshm_put",
            "osu_oshm_put_nb",
            "osu_oshm_collect",
            "osu_oshm_atomics",
            "osu_oshm_barrier",
            "osu_oshm_put_mr",
            "osu_oshm_fcollect",
            "osu_xccl_latency",
            "osu_xccl_bibw",
            "osu_xccl_bw",
            "osu_xccl_reduce_scatter",
            "osu_xccl_alltoall",
            "osu_xccl_allgather",
            "osu_xccl_reduce",
            "osu_xccl_bcast",
            "osu_xccl_allreduce",
        ),
        multi=True,
        description="workloads available",
    )

    variant(
        "version",
        default="7.5.1",
        values=("latest", "7.5", "7.5.1"),
        description="app version",
    )
    variant(
        "xccl",
        default=False,
        description="Enable NCCL/RCCL support",
    )
    variant(
        "papi",
        default=False,
        description="Enable PAPI support",
    )
    variant(
        "graphing",
        default=False,
        description="Enable graphing support",
    )
    variant(
        "managed",
        default=False,
        description="Enable Managed Memory support",
    )
    variant(
        "papi_events",
        default = "PAPI_TOT_INS,PAPI_TOT_CYC,PAPI_L1_DCM,PAPI_L1_ICM,PAPI_L2_DCM",
        description="PAPI events"
    )
    variant(
        "papi_output",
        default="papi.out",
        description="PAPI output file"
    )
    variant(
        "graph_type",
        default="png",
        description="Graph type"
    )

    maintainers("nhanford")

    def compute_applications_section(self):
        import yaml
        import os
        import sys
        import glob

        dest_dir = None
        for i, arg in enumerate(sys.argv):
            if arg == 'init' and i + 1 < len(sys.argv):
                dest_dir = sys.argv[i + 1]
                break

        if not dest_dir:
            return

        # read packages.yaml
        yaml_path = os.path.join(dest_dir, 'auxiliary_software_files', 'packages.yaml')
        modules = []
        if os.path.exists(yaml_path):
            with open(yaml_path, 'r') as f:
                data = yaml.safe_load(f)
                # get mpi externals
                mpi_externals = data.get('packages', {}).get('nvhpc', {}).get('externals', [])
                #mpi_externals = data.get('packages', {}).get('mpi', {}).get('externals', [])
                if mpi_externals:
                    modules = mpi_externals[0].get('modules', [])

        setup_env_cmd = "echo ''; "
        for m in modules:
            setup_env_cmd += f"module load {m};"
        self.add_experiment_variable("pre_run_cmds", setup_env_cmd, False)

        #########################################################################
        #print("\nDEBUG: --- self Attributes List ---")
        #for attr in dir(self):
        #    if not attr.startswith('__'):
        #        try:
        #            value = getattr(self, attr)
        #            if not callable(value):
        #                print(f"DEBUG: {attr} = {value}")
        #        except:
        #            print(f"DEBUG: {attr} = [Access Error]")
        #print("DEBUG: ----------------------------\n")
        #########################################################################

        graph_type_val = "png"
        papi_events_val = ""
        papi_output_val = ""

        if self.spec.satisfies("+papi"):
            papi_val = self.spec.variants.get("papi_events")
            if papi_val:
                #papi_events_val = str(papi_val[0]).replace(":", ",")
                papi_events_val = str(self.spec.variants["papi_events"][0]).replace(":", ",")

            papi_output = self.spec.variants.get("papi_output")
            if papi_output:
                #papi_output_val = str(papi_output[0])
                papi_output_val = str(self.spec.variants["papi_output"][0])

        #if self.spec.satisfies("+graphing"):
        #    graph_type = self.spec.variants.get("graph_type")
        #    if graph_type:
        #        graph_type_val = str(graph_type[0])
        if self.spec.satisfies("+graphing"):
            graph_type_val = str(self.spec.variants["graph_type"][0])

        run_args = []
        if self.spec.satisfies("+rocm"):
            run_args.append("-d rocm")

        if self.spec.satisfies("+cuda"):
            if self.spec.satisfies("+managed"):
                run_args.append("-d managed")
            else:
                run_args.append("-d cuda")

        if self.spec.satisfies("+papi"):
            run_args.append(f"-P {papi_events_val}:{papi_output_val}")

        if self.spec.satisfies("+graphing"):
            run_args.append(f"-G {graph_type_val}")

        self.add_experiment_variable("oshm_mem_type", "heap", False)

        self.add_experiment_variable("additional_args", " ".join(run_args), False)

#<<<<<<< HEAD
        num_nodes = {"n_nodes": 2}
#=======
#        num_nodes = {"n_nodes": 2, "n_ranks": 1}
#
#>>>>>>> upstream/develop
        #if self.spec.satisfies("exec_mode=test"):
        #    for pk, pv in num_nodes.items():
        #        self.add_experiment_variable(pk, pv, True)

        n_resources = 2
        n_ranks = 2
        if self.spec.satisfies("+rocm") or self.spec.satisfies("+cuda"):
            self.add_experiment_variable("n_gpus", 1, True)
        else:
            self.add_experiment_variable("n_nodes", 2, True)

        #n_resources = "{" + resource + "}"
        self.set_required_variables(
            n_resources=n_resources, process_problem_size="", total_problem_size=""
        )
        self.add_experiment_variable("n_ranks", n_ranks, True)

        # set osu-micro-benchmarks_path using prepend_path
        prep_dir = None
        for i, arg in enumerate(sys.argv):
            if arg.startswith('prepend_path='):
                path_str = arg.split('=', 1)[1].strip('"')
                prep_dir = path_str.split(":")[0]
                break
        if prep_dir is not None: 
            matches = glob.glob(prep_dir)
            if not matches:
                raise RuntimeError(f"Cannot find osu-micro-benchmarks : {prep_dir}")
            osu_base_path = matches[0]
            self.add_experiment_variable("osu-micro-benchmarks_path", osu_base_path, False)


    def compute_package_section(self):
        pkg_spec = f"osu-micro-benchmarks{self.determine_version()}"

        if self.spec.satisfies("+xccl"):
            pkg_spec += "+xccl"

        if self.spec.satisfies("+papi"):
            pkg_spec += "+papi"

        if self.spec.satisfies("+graphing"):
            pkg_spec += "+graphing"

        if self.spec.satisfies("+managed"):
            pkg_spec += "+managed"

        self.add_package_spec(self.name, [pkg_spec])
