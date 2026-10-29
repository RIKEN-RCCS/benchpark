# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from ramble.appkit import *


class Ffb(ExecutableApplication):
    """Define FFB application

    The application holds no knowledge of the machine it runs on. It used to
    branch on SLURM_JOB_PARTITION (and before that on RAMBLE_ROOT) when it
    was imported, so `ramble workspace setup` in a compute-node job and
    `ramble on` on a login node took different branches and stopped with
    "Mismatch on experiment hash". The machine-dependent parts are set by
    the experiment instead (RIKEN-RCCS/benchpark#54):

      * which input: one workload per input, chosen by the experiment;
      * where the input is: ffb_input_url;
      * how to launch: the system's mpi_command;
      * where rank 0 writes its log: ffb_log;
      * shell setup before the launch: ffb_setup.
    """

    name = "FFB"

    maintainers("ando")

    tags('fluid-dynamics')

    # Each input is partitioned for a fixed number of ranks (MESH.P0001,
    # ...), so it is tied to the run configuration that uses it.
    inputs = {
        # 4 domains, the GPU run on riken-gh200.
        "cavity_7_8M": (
            "benchmark-input-7.8M",
            "2db68022eb463a328ca69dc949f6abf53126d2f177281d6b3533d7c85c6da5f3",
        ),
        # 16 domains, the CPU runs on riken-genoa and riken-fugaku.
        "cavity_2_0M": (
            "benchmark-input-2.0M",
            "ac8021b07012f78452e7a964712a849ed8e50364352a3f65677c4eb499e1c501",
        ),
    }

    executable("setup", "{ffb_setup}", use_mpi=False)

    executable("cpdata", "cp {input}/* .", use_mpi=False)

    executable("execute", "les3x.mpi", use_mpi=True)

    # Rank 0's log is les3x.log.P0001 on riken-gh200, the experiment's own
    # output on riken-genoa and fjmpioutdir/bmexe.1.0 on riken-fugaku
    # (Fujitsu MPI's -std-proc). Copy it to one file, converting Fortran's
    # D exponents, so that the figure of merit reads the same place
    # everywhere.
    executable(
        "collect",
        'sed -e "s/D+/E+/g" -e "s/D-/E-/g" {ffb_log}',
        use_mpi=False,
        redirect="{experiment_run_dir}/ffb.log",
        output_capture=OUTPUT_CAPTURE.STDOUT,
    )

    for _workload, (_input, _sha256) in inputs.items():
        input_file(
            _input,
            url="{ffb_input_url}",
            sha256=_sha256,
            description='Benchmark set for FFB',
        )

        workload(
            _workload,
            executables=["setup", "cpdata", "execute", "collect"],
            input=_input,
        )

        workload_variable(
            'input',
            default='{' + _input + '}',
            description='input/ : benchmark-input root directory',
            workloads=[_workload],
        )

    workload_variable(
        'ffb_input_url',
        default='',
        description='Location of the input archive; set by the experiment',
        workloads=list(inputs),
    )
    workload_variable(
        'ffb_log',
        default='{experiment_run_dir}/les3x.log.P0001',
        description="Rank 0's log, which carries the timing summary",
        workloads=list(inputs),
    )
    workload_variable(
        'ffb_setup',
        default=':',
        description='Shell command run before the launch, e.g. ulimit',
        workloads=list(inputs),
    )

    figure_of_merit('Figure of Merit (FOM)', log_file='{experiment_run_dir}/ffb.log', fom_regex=r'^\s+1\s+USRT:TIME-LOOP\s+(?P<fom>[-+]?([0-9]*[.])?[0-9]+([eED][-+]?[0-9]+)?)', group_name='fom', units='')

    success_criteria(
        name="fom_below_400s",
        mode="fom_comparison",
        fom_name="Figure of Merit (FOM)",
        formula="{value} <= 400"
    )
