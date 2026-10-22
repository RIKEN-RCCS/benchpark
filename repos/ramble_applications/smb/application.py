# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import sys

from ramble.appkit import *


class Smb(ExecutableApplication):
    """Sandia microbenchmarks"""
    name = "Sandia microbenchmarks"

    executable('p1', 'mpi_overhead', use_mpi=True)
    executable('p2', 'msgrate -n {ppn}', use_mpi=True)
    executable('p3', 'rma_mt_mpi -n {ppn} -t {threads} -i {iterations}', use_mpi=True)

    workload('mpi_overhead', executables=['p1'])
    workload('msgrate', executables=['p2'])
    workload('rma_mt', executables=['p2'])
    workload('rma_mt_mpi', executables=['p3'])

    workload_variable('ppn', default='1',
                   description='Number of procs per node',
                   workloads=['msgrate', 'rma_mt', 'rma_mt_mpi'])

    # rma_mt_mpi moves the messages from this many threads per rank; its own
    # default is zero threads, which starts none and never finishes.
    workload_variable('threads', default='1',
                   description='Number of threads doing communication per rank',
                   workloads=['rma_mt_mpi'])
    workload_variable('iterations', default='4096',
                   description='Iterations per test (the benchmark default)',
                   workloads=['rma_mt_mpi'])

    figure_of_merit('single direction',
                   log_file='{experiment_run_dir}/{experiment_name}.out',
                   fom_regex=r'single direction:\s+(?P<fom>[0-9]+\.[0-9]*)',
                  group_name='fom', units='')
    #TODO:fix this FOM. Not sure what's causing it to not detect
    figure_of_merit('overhead',
                    log_file='{experiment_run_dir}/{experiment_name}.out',
                    fom_regex=r'(?:[0-9]+\.?[0-9]* +){4}(?P<fom>[0-9]+\.[0-9]*)',
                    #fom_regex=r'avail\(%\)(?:\s|\t)*\n\s*(?:[0-9]+\.*[0-9]*\s*){4}(?P<fom>[0-9]+\.*[0-9]*)',
                   group_name='fom', units='')

    # rma_mt_mpi prints its two results with the name padded before the
    # colon ("single direction : 1234.56", "halo-exchange    : 789.01"),
    # which the patterns above do not match.
    figure_of_merit('single direction (rma_mt_mpi)',
                   log_file='{experiment_run_dir}/{experiment_name}.out',
                   fom_regex=r'single direction\s+:\s+(?P<fom>[0-9]+\.[0-9]*)',
                   group_name='fom', units='messages/s')
    figure_of_merit('halo-exchange (rma_mt_mpi)',
                   log_file='{experiment_run_dir}/{experiment_name}.out',
                   fom_regex=r'halo-exchange\s+:\s+(?P<fom>[0-9]+\.[0-9]*)',
                   group_name='fom', units='messages/s')

    figure_of_merit('pair based',
                    log_file='{experiment_run_dir}/{experiment_name}.out',
                    fom_regex=r'pair-based:\s+(?P<fom>[0-9]+\.[0-9]*)',
                   group_name='fom', units='')

    figure_of_merit('pre-post',
                    log_file='{experiment_run_dir}/{experiment_name}.out',
                    fom_regex=r'\s*pre-post:\s+(?P<fom>[0-9]+\.[0-9]*)',
                   group_name='fom', units='')

    figure_of_merit('all-start',
                    log_file='{experiment_run_dir}/{experiment_name}.out',
                    fom_regex=r'\s*all-start:\s+(?P<fom>[0-9]+\.[0-9]*)',
                   group_name='fom', units='')
    #success_criteria('pass', mode='string', match=r'.*', file='{experiment_run_dir}/{experiment_name}.out')
