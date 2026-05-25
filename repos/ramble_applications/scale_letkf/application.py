# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import sys
from ramble.appkit import *

class ScaleLetkf(ExecutableApplication):
    """SCALE-LETKF benchmark execution"""
    name = "scale-letkf"

    # set up
    executable(name='dir_setup',
               template='cp -Lr {scale-letkf}/share/{benchmark_dir}/* . && bash ./prep.sh',
               use_mpi=False,
               index=0)
    executable(name='env_setup',
               template='{tuning_cmds}',
               use_mpi=False,
               index=1)

    # expand files
    executable(name='expand1',
               template='tar zxf {scale_database_path}',
               use_mpi=False,
               index=2)
    executable(name='expand2',
               template='tar zxf {dataset_path}',
               use_mpi=False,
               index=3)

    # execution
    executable(name='pp',
               template='{scale-letkf}/bin/scale-rm_pp_ens {pp_conf}',
               variables={'n_resources': '{pp_ranks}'},
               use_mpi=True,
               index=4)
    executable(name='init',
               template='{scale-letkf}/bin/scale-rm_init_ens {init_conf}',
               variables={'n_resources': '{n_ranks}'},
               use_mpi=True,
               index=5)
    executable(name='run',
               template='{scale-letkf}/bin/scale-rm_ens {run_conf}',
               variables={'n_resources': '{n_ranks}'},
               use_mpi=True,
               index=6)
    executable(name='letkf',
               template='{scale-letkf}/bin/letkf {letkf_conf}',
               variables={'n_resources': '{n_ranks}'},
               use_mpi=True,
               index=7)

    workload('benchmark', ['dir_setup', 'env_setup', 'expand1', 'expand2', 'pp', 'init', 'run', 'letkf'])

    figure_of_merit('Figure of Merit (FOM): SCALE',
                    log_file='{experiment_run_dir}/{experiment_name}.out',
                    fom_regex=r'##### TIMER # SCALE-RM\s+(?P<fom_scale>[0-9.]+)',
                    group_name='fom_scale',
                    units='sec')

    figure_of_merit('Figure of Merit (FOM): LETKF',
                    log_file='{experiment_run_dir}/{experiment_name}.out',
                    fom_regex=r'##### TIMER # LETKF\s+(?P<fom_letkf>[0-9.]+)',
                    group_name='fom_letkf',
                    units='sec')
