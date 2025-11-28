# Copyright 2022-2025 The Ramble Authors
#
# Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
# https://www.apache.org/licenses/LICENSE-2.0> or the MIT license
# <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your
# option. This file may not be copied, modified, or distributed
# except according to those terms.

from ramble.appkit import *


class Ffb(ExecutableApplication):
    """Define FFB application"""

    name = "FFB"

    maintainers("ando")

    pre_cmds = [
    	"module purge",
    	"module load system/qc-gh200 nvhpc/24.3",
    ]
 

    executable("execute",
       "module purge && module load system/qc-gh200 nvhpc/24.3 && cp {input}/* . && mpiexec -np {n_ranks} les3x.mpi",
       use_mpi=False,
    )

    input_file('benchmark-input',
               url='file:///lvs0/rccs-sdt/kazuto.ando/apps/ffb/benchmark-input.tar.gz',
               sha256='2db68022eb463a328ca69dc949f6abf53126d2f177281d6b3533d7c85c6da5f3',
               description='Benchmark set for FFB')

    workload("cavity", executables=["execute"], input='benchmark-input')

    workload_variable('input', default='{benchmark-input}',
                      description='input/ : benchmark-input root directory',
                      workloads=['cavity'])

    figure_of_merit('Figure of Merit (FOM)', log_file='{experiment_run_dir}/les3x.log.P0001', fom_regex=r'^\s+1\s+USRT:TIME-LOOP\s+(?P<fom>[-+]?([0-9]*[.])?[0-9]+([eED][-+]?[0-9]+)?)', group_name='fom', units='')

    #success_criteria('pass', mode='string', match=r'SUCCESSFULLY TERMINATED', file='{experiment_run_dir}/les3x.log.P0001')
    success_criteria(
        name="fom_below_100",
        mode="fom_comparison",
        fom_name="Figure of Merit (FOM)",
        formula="{value} <= 100"
    )

