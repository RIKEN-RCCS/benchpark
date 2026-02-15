from ramble.appkit import *
from ramble.app.builtin.nccl_tests import NcclTests as NcclTestsBase

class NcclTests(NcclTestsBase):

    # The following five executable are defined in the parent class, but they override it:
    # The workload definition uses the parent class's definition as is.
    executable(
        "all-to-all-execute",
        template=["{pre_run_cmds}\n{mpi_command} alltoall_perf {additional_args}"],
        use_mpi=True,
    )
    executable(
        "all-reduce-execute",
        template=["{pre_run_cmds}\n{mpi_command} all_reduce_perf {additional_args}"],
        use_mpi=True,
    )
    executable(
        "all-gather-execute",
        template=["{pre_run_cmds}\n{mpi_command} all_gather_perf {additional_args}"],
        use_mpi=True,
    )
    executable(
        "reduce-scatter-execute",
        template=["{pre_run_cmds}\n{mpi_command} reduce_scatter_perf {additional_args}"],
        use_mpi=True,
    )
    executable(
        "send-recv-execute",
        template=["{pre_run_cmds}\n{mpi_command} sendrecv_perf {additional_args}"],
        use_mpi=True,
    )
    # Define five executables and workloads that are not defined in the parent class.
    executable(
        "broadcast-execute",
        template=["{pre_run_cmds}\n{mpi_command} broadcast_perf {additional_args}"],
        use_mpi=True,
    )
    workload("broadcast", executables=["broadcast-execute"])

    executable(
        "gather-execute",
        template=["{pre_run_cmds}\n{mpi_command} gather_perf {additional_args}"],
        use_mpi=True,
    )
    workload("gather", executables=["gather-execute"])

    executable(
        "reduce-execute",
        template=["{pre_run_cmds}\n{mpi_command} reduce_perf {additional_args}"],
        use_mpi=True,
    )
    workload("reduce", executables=["reduce-execute"])

    executable(
        "scatter-execute",
        template=["{pre_run_cmds}\n{mpi_command} scatter_perf {additional_args}"],
        use_mpi=True,
    )
    workload("scatter", executables=["scatter-execute"])

    executable(
        "hypercube-execute",
        template=["{pre_run_cmds}\n{mpi_command} hypercube_perf {additional_args}"],
        use_mpi=True,
    )
    workload("hypercube", executables=["hypercube-execute"])

    all_workloads = NcclTestsBase.all_workloads + [
        "broadcast", "gather", "reduce", "scatter", "hypercube"
    ]

