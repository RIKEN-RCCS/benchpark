# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import os

from ramble.appkit import *


class SalmonTddft(ExecutableApplication):
    """Salmon-tddft benchmark"""
    name = 'salmon-tddft'

    tags = ['mpi']

    if 'cloud.r-ccs.riken.jp' in os.environ['HOSTNAME']:
        url = 'file:///lvs0/dne1/rccs-nghpcadu/CX_input/SALMON/SALMON.tar.gz'

        exec_pp = 'module purge && module load system/qc-gh200 && module load nvhpc-hpcx-cuda12/25.7 && cp {input_path}/* .'

        exec_gs = 'salmon < Si-1-1-1.nml'
        exec_rt = 'salmon < Si-1-1-1-tddft.nml'
        
    else:
        url = 'file:///vol0003/rccs-sdt/data/a01010/benchmark_data/SALMON.tar.gz'

        exec_pp = 'cp {input_path}/* .'

        exec_gs = '-stdin Si-1-1-1.nml salmon'
        exec_rt = '-stdin Si-1-1-1-tddft.nml salmon'

    input_file(
        'benchmark-input',
        url=url,
        sha256='2bb828d9c6393bcaf4b79ba2cd0f301a0318b919df90274679ee5b5a12fad571',
        description='Benchmark inputs for SALMON',
    )

    executable('pre-process', exec_pp, use_mpi=False)

    executable('rename-data', 'mv data_for_restart restart', use_mpi=False)

    executable('start-timer-gs', 'gs_start_time=$(date +%s.%N)', use_mpi=False)
    executable('execute_gs', exec_gs, use_mpi=True)
    executable(
        'stop-timer-gs', 
        'gs_end_time=$(date +%s.%N) && gs_elapsed=$(echo "${gs_end_time} - ${gs_start_time}" | bc -l)', 
        use_mpi=False
    )

    executable('start-timer-rt', 'rt_start_time=$(date +%s.%N)', use_mpi=False)
    executable('execute_rt', exec_rt, use_mpi=True)
    executable(
        'stop-timer-rt', 
        'rt_end_time=$(date +%s.%N) && rt_elapsed=$(echo "${rt_end_time} - ${rt_start_time}" | bc -l)', 
        use_mpi=False
    )

    executable(
        'calc-total-time', 
        'total_elapsed=$(echo "${gs_elapsed} + ${rt_elapsed}" | bc -l) && echo "total_elapsed_time: $total_elapsed"', 
        use_mpi=False
    )

    workload(
        'Si-1-1-1', 
        executables=[
            'pre-process',
            'start-timer-gs',
            'execute_gs',
            'stop-timer-gs',
            'rename-data',
            'start-timer-rt',
            'execute_rt',
            'stop-timer-rt',
            'calc-total-time',
        ], 
        input='benchmark-input',
    )

    workload_variable(
        'input_path',
        default='{benchmark-input}/Si-1-1-1/input',
        description='Input path for Si-1-1-1',
        workload='Si-1-1-1'
    )

    workload_variable(
        'input_data_gs',
        default='Si-1-1-1.nml',
        description='Input data for gs',
        workload='Si-1-1-1'
    )

    workload_variable(
        'input_data_rt',
        default='Si-1-1-1-tddft.nml',
        description='Input data for rt',
        workload='Si-1-1-1'
    )

    figure_of_merit(
        'Figure of Merit (FOM)', 
        log_file='{experiment_run_dir}/{experiment_name}.out', 
        fom_regex=r'^total_elapsed_time: (?P<fom>[-+]?[0-9]*\.?[0-9]+)$', 
        group_name='fom', 
        units='s'
    )

    success_criteria(
        'pass', 
        mode='string', 
        match=r'total calculation time', 
        file='{experiment_run_dir}/{experiment_name}.out'
    )

    def setup(self):
        if self.system_name == "fugaku_fj":
            self.software_spec = "salmon-tddft %fj"
        else:
            self.software_spec = "salmon-tddft"
