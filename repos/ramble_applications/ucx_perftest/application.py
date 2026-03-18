# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import sys

from ramble.appkit import *


class UcxPerftest(ExecutableApplication):
    """UCX perftest benchmark"""
    name = "ucx_perftest"

    executable(
        'run_server',
        'srun -N 1 -n 1 -w ${server_node} ucx_perftest {server_opts} & sleep 5',
        use_mpi=False,
    )

    executable(
        'run_client',
        'srun -N 1 -n 1 -w ${client_node} ucx_perftest ${server_node} {client_opts}',
        use_mpi=False,
    )

    executable(
        'set_environments',
        '{pre_run_cmds}\n'
        'nodes=($(scontrol show hostname $SLURM_NODELIST))\n'
        'server_node=${nodes[0]}\n'
        'client_node=${nodes[1]}\n'
        'export UCX_TLS={UCX_TLS};\n'
        'export UCX_SELF_DEVICES={UCX_SELF_DEVICES};\n'
        'export UCX_SHM_DEVICES={UCX_SHM_DEVICES};\n'
        'export UCX_NET_DEVICES={UCX_NET_DEVICES}; ',
        use_mpi=False,
    )

    workload(
        'ucx_perftest',
        executables=['set_environments', 'run_server', 'run_client'],
    )

    workload_variable(
        'server_opts',
        default='-c 0',
        description='Options for server',
        workloads=['ucx_perftest']
    )

    workload_variable(
        'client_opts',
        default='-c 1 -t tag_lat',
        description='Options for client',
        workloads=['ucx_perftest']
    )

