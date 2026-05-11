# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import os

from ramble.appkit import *


class Ffb(ExecutableApplication):
    """Define FFB application"""

    name = "FFB"

    maintainers("ando")

    tags('fluid-dynamics')

    if '/lvs' in os.environ["RAMBLE_ROOT"]:
        if 'qc-gh200' in os.environ["SLURM_JOB_PARTITION"]:
            cmd = "module purge && module load system/qc-gh200 nvhpc/24.3 && mpiexec -np {n_ranks} les3x.mpi"
            chksum = '2db68022eb463a328ca69dc949f6abf53126d2f177281d6b3533d7c85c6da5f3'
            url = 'file:///lvs0/rccs-sdt/kazuto.ando/apps/ffb/benchmark-input-7.8M.tar.gz'
            executables = ["cpdata", "execute"]
        elif 'genoa' in os.environ["SLURM_JOB_PARTITION"]:
            cmd = "ulimit -s unlimited && module purge && module load system/genoa mpi/openmpi-x86_64 && mpiexec -np {n_ranks} les3x.mpi"
            chksum = 'ac8021b07012f78452e7a964712a849ed8e50364352a3f65677c4eb499e1c501'
            url = 'file:///lvs0/rccs-sdt/kazuto.ando/apps/ffb/benchmark-input-2.0M.tar.gz'
            executables = ["cpdata", "execute", "replace_cpu"]
        use_mpi = False
    else:
        cmd = "les3x.mpi"
        use_mpi = True
        url = 'file:///vol0003/rccs-sdt/data/a01008/apps/ffb/benchmark-input.tar.gz'
        chksum = 'ac8021b07012f78452e7a964712a849ed8e50364352a3f65677c4eb499e1c501'
        executables = ["cpdata", "execute", "replace"]

    executable("cpdata", "cp {input}/* .", use_mpi=False)

    executable(
        "execute",
        cmd,
        use_mpi=use_mpi
    )

    executable("replace", "cp {experiment_run_dir}/fjmpioutdir/bmexe.1.0 {experiment_run_dir}/les3x.log.P0001 && sed -i -e \"s/D+/E+/\" -e \"s/D-/E-/\" {experiment_run_dir}/les3x.log.P*", use_mpi=False)
    executable("replace_cpu", "cp {experiment_run_dir}/ffb_*.out {experiment_run_dir}/les3x.log.P0001 && sed -i -e \"s/D+/E+/\" -e \"s/D-/E-/\" {experiment_run_dir}/les3x.log.P*", use_mpi=False)

    input_file('benchmark-input',
               url=url,
               sha256=chksum,
               description='Benchmark set for FFB')

    workload("cavity",
             executables=executables,
             input="benchmark-input")

    workload_variable('input', default='{benchmark-input}',
                      description='input/ : benchmark-input root directory',
                      workloads=['cavity'])

    figure_of_merit('Figure of Merit (FOM)', log_file='{experiment_run_dir}/les3x.log.P0001', fom_regex=r'^\s+1\s+USRT:TIME-LOOP\s+(?P<fom>[-+]?([0-9]*[.])?[0-9]+([eED][-+]?[0-9]+)?)', group_name='fom', units='')

    success_criteria(
        name="fom_below_400s",
        mode="fom_comparison",
        fom_name="Figure of Merit (FOM)",
        formula="{value} <= 400"
    )

