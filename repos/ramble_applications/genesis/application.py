# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import sys
from ramble.appkit import *

class Genesis(ExecutableApplication):
    name = "GENESIS"

    tags = ['molecular-dynamics', 'mpi']

    executable(
        'genesis',
        "bash -lc 'cd $(dirname {input_file}) && spdyn $(basename {input_file})'",
        use_mpi=True
    )

    executable(
        'fix_path',
        template=[
            "sed -i 's|../../../build/cryoEM/go_model/|{build_path}/|g' inp",
        ],
        workloads=['cryoEM']
    )

    input_file(
        'genesis-benchmark',
        url='https://github.com/genesis-release-r-ccs/genesis_benchmark_input/archive/refs/tags/v1.0.0.tar.gz',
        sha256='13a04449f4036e38a640fd44adb08c723942515ecf512e7c64161c4ff96c8b5c',
        description='Benchmark input set for GENESIS'
    )

    # input_file(
    #     'genesis-cx_input',
    #     url='file:///lvs0/dne1/rccs-nghpcadu/CX_input/CX_Input-20260317.tar.gz',
    #     sha256='e257ef4ccc920bbcdc807551dd46497618c03d7ce93bf8d88b866c7a54b4f4b9',
    #     description='CX_Input input set 20260317'
    # )

    input_file(
        'genesis-tests',
        url='https://github.com/genesis-release-r-ccs/genesis/archive/refs/tags/v2.1.5.tar.gz',
        description='GENESIS v2.1.5 source tree containing regression test inputs'
    )

    # workload(
    #     'Lysozyme',
    #     executables=['genesis'],
    #     input='genesis-cx_input'
    # )

    workload(
        'DHFR',
        executables=[ 'genesis'],
        input='genesis-benchmark'
    )

    workload(
        'ApoA1',
        executables=[ 'genesis'],
        input='genesis-benchmark'
    )

    workload(
        'UUN',
        executables=[ 'genesis'],
        input='genesis-benchmark'
    )

    workload(
        'cryoEM',
        executables=[ 'fix_path', 'genesis'],
        input='genesis-tests'
    )

    # workload_variable(
    #     'input_file',
    #     '{genesis-cx_input}/GENESIS/Evaluation_duplication/orig_1dalltoall_2nodes/lyso_vres_org.inp',
    #     'Lysozyme duplication system input file for sol 1x1x1',
    #     workload='Lysozyme'
    # )

    workload_variable(
        'input_file',
        '{genesis-benchmark}/npt/genesis2.0beta/jac_amber/p{n_ranks}.inp',
        'DHFR input file',
        workload='DHFR'
    )

    workload_variable(
        'input_file',
        '{genesis-benchmark}/npt/genesis2.0beta/apoa1/p{n_ranks}.inp',
        'ApoA1 input file',
        workload='ApoA1'
    )

    workload_variable(
        'input_file',
        '{genesis-benchmark}/npt/genesis2.0beta/uun/p{n_ranks}.inp',
        'UUN input file',
        workload='UUN'
    )

    workload_variable(
        'input_file',
        '{genesis-tests}/tests/regression_test/test_spdyn/cryoEM/All_atom/inp',
        'CryoEM input file',
        workload='cryoEM'
    )

    figure_of_merit(
        'Figure of Merit (FOM)',
        log_file='{experiment_run_dir}/{experiment_name}.out',
        fom_regex=r'^\s+dynamics\s+=\s+(?P<fom>[-+]?([0-9]*[.])?[0-9]+([eED][-+]?[0-9]+)?)',
        group_name='fom',
        units=''
    )

    success_criteria(
        'pass',
        mode='string',
        match=r'Figure of Merit \(FOM\)',
        file='{experiment_run_dir}/{experiment_name}.out'
    )
