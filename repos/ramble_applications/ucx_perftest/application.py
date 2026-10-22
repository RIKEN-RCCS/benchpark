# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from ramble.appkit import *


class UcxPerftest(ExecutableApplication):
    """ucx_perftest, UCX's point-to-point benchmark: a server on the first
    node of the allocation, a client on the second (Slurm, srun)."""

    name = "ucx_perftest"

    tags("network-benchmark", "communication-benchmark")

    with when("package_manager_family=spack"):
        software_spec("ucx_perftest", pkg_spec="ucx")

    executable(
        "set_environments",
        "nodes=($(scontrol show hostname $SLURM_JOB_NODELIST))\n"
        "server_node=${nodes[0]}\n"
        "client_node=${nodes[1]}\n"
        "export UCX_TLS={UCX_TLS}\n"
        "export UCX_SELF_DEVICES={UCX_SELF_DEVICES}\n"
        "export UCX_SHM_DEVICES={UCX_SHM_DEVICES}\n"
        "export UCX_NET_DEVICES={UCX_NET_DEVICES}",
        use_mpi=False,
    )

    executable(
        "run_server",
        "srun -N 1 -n 1 -w ${server_node} {step_opts} ucx_perftest {server_opts} &\n"
        "sleep 5",
        use_mpi=False,
    )

    # One line, so that ramble's redirection of the executable's output
    # (which it appends to the last line of a template) catches the
    # client's report.
    executable(
        "run_client",
        "srun -N 1 -n 1 -w ${client_node} {step_opts} ucx_perftest ${server_node} {client_opts}",
        use_mpi=False,
    )

    executable("wait_server", "wait", use_mpi=False)

    workload(
        "ucx_perftest",
        executables=["set_environments", "run_server", "run_client", "wait_server"],
    )

    workload_variable(
        "server_opts",
        default="-c 0",
        description="Options for the server",
        workloads=["ucx_perftest"],
    )
    workload_variable(
        "client_opts",
        default="-c 1 -t tag_lat",
        description="Options for the client (the test, its sizes and iterations)",
        workloads=["ucx_perftest"],
    )
    workload_variable(
        "step_opts",
        default="",
        description="Options for the srun step of each side, e.g. --gpus 1",
        workloads=["ucx_perftest"],
    )
    for env_name in ("UCX_TLS", "UCX_SELF_DEVICES", "UCX_SHM_DEVICES", "UCX_NET_DEVICES"):
        workload_variable(
            env_name,
            default="all",
            description=f"Value of {env_name} for both sides",
            workloads=["ucx_perftest"],
        )

    # ucx_perftest prints one line per test:
    #   +--------------+--------------+------------------------------+---------------------+-----------------------+
    #   |              |              |       overhead (usec)        |   bandwidth (MB/s)  |  message rate (msg/s) |
    #   | # iterations | 50.0%ile | average | overall | average | overall | average | overall |
    #   Final:    1000000     1.218     1.221     1.221    6.26    6.26   818889   818889
    final_regex = (
        r"Final:\s+(?P<iters>[0-9]+)\s+(?P<lat_p50>[0-9.]+)\s+(?P<lat_avg>[0-9.]+)\s+(?P<lat_all>[0-9.]+)"
        r"\s+(?P<bw_avg>[0-9.]+)\s+(?P<bw_all>[0-9.]+)\s+(?P<rate_avg>[0-9.]+)\s+(?P<rate_all>[0-9.]+)"
    )
    log_file = "{experiment_run_dir}/{experiment_name}.out"
    figure_of_merit("Iterations", log_file=log_file, fom_regex=final_regex, group_name="iters", units="")
    figure_of_merit("Latency P50", log_file=log_file, fom_regex=final_regex, group_name="lat_p50", units="us")
    figure_of_merit("Latency", log_file=log_file, fom_regex=final_regex, group_name="lat_avg", units="us")
    figure_of_merit("Latency Overall", log_file=log_file, fom_regex=final_regex, group_name="lat_all", units="us")
    figure_of_merit("Bandwidth", log_file=log_file, fom_regex=final_regex, group_name="bw_avg", units="MB/s")
    figure_of_merit("Bandwidth Overall", log_file=log_file, fom_regex=final_regex, group_name="bw_all", units="MB/s")
    figure_of_merit("Message Rate", log_file=log_file, fom_regex=final_regex, group_name="rate_avg", units="msg/s")
    figure_of_merit("Message Rate Overall", log_file=log_file, fom_regex=final_regex, group_name="rate_all", units="msg/s")

    success_criteria("final_line", mode="string", match=r"Final:", file=log_file)
