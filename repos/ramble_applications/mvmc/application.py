# Copyright 2026
# SPDX-License-Identifier: Apache-2.0

from ramble.appkit import *


class Mvmc(ExecutableApplication):
    """Minimal mVMC Standard-mode benchmark for Benchpark/Ramble."""

    name = "mvmc"
    tags = ["materials", "quantum", "monte-carlo", "mpi"]

    # Avoid a here-document here. Ramble appends stdout/stderr redirection to
    # executable commands, which can break a multi-line `cat <<EOF` construct.
    # This one-line command creates both the mVMC output directory and StdFace.def.
    executable(
        "make-input",
        r"""bash -c 'mkdir -p output && printf "%s\n" "L = {L}" "Lsub={Lsub}" "model = \"{model}\"" "lattice = \"{lattice}\"" "J = {J}" "2 Sz = {two_sz}" "NMPtrans={nmptrans}" > StdFace.def'""",
        use_mpi=False,
    )

    executable(
        "run-mvmc",
        "vmc.out -s StdFace.def",
        use_mpi=True,
    )

    # Copy mVMC's output files to top-level files used only by Ramble analysis.
    # This avoids asking Ramble to pre-touch files under output/, because output/
    # may not exist when the job script begins.
    executable(
        "collect-results",
        r"""bash -c 'for f in zvo_out_001.dat zvo_CalcTimer.dat; do if [ -f output/$f ]; then cp -f output/$f mvmc_$f; else : > mvmc_$f; echo "missing output/$f" >&2; fi; done'""",
        use_mpi=False,
    )

    workload(
        "standard",
        executables=["make-input", "run-mvmc", "collect-results"],
    )

    workload_variable(
        "L",
        default="16",
        description="Number of sites in the Heisenberg chain.",
        workloads=["standard"],
    )

    workload_variable(
        "Lsub",
        default="4",
        description="mVMC Standard-mode Lsub parameter.",
        workloads=["standard"],
    )

    workload_variable(
        "model",
        default="Spin",
        description="mVMC Standard-mode model.",
        workloads=["standard"],
    )

    workload_variable(
        "lattice",
        default="chain lattice",
        description="mVMC Standard-mode lattice.",
        workloads=["standard"],
    )

    workload_variable(
        "J",
        default="1.0",
        description="Nearest-neighbor spin coupling.",
        workloads=["standard"],
    )

    workload_variable(
        "two_sz",
        default="0",
        description="Value written as '2 Sz' in StdFace.def.",
        workloads=["standard"],
    )

    workload_variable(
        "nmptrans",
        default="1",
        description="mVMC Standard-mode NMPtrans parameter.",
        workloads=["standard"],
    )

    # Treat the mVMC completion message in Ramble's stdout file as success.
    success_criteria(
        "pass",
        mode="string",
        match=r"End  : Optimize VMC parameters.",
        file="{experiment_run_dir}/{experiment_name}.out",
    )

    # mVMC writes these files under output/. The collect-results executable copies
    # them to top-level analysis files so Ramble does not need output/ to exist
    # before executable commands begin.
    figure_of_merit(
        "energy",
        fom_regex=r"^\s*(?P<energy>[-+0-9.Ee]+)\s+[-+0-9.Ee]+\s+[-+0-9.Ee]+\s*$",
        group_name="energy",
        log_file="{experiment_run_dir}/mvmc_zvo_out_001.dat",
        units="",
    )

    figure_of_merit(
        "total-time",
        fom_regex=r"^\s*All\s+\[0\]\s+(?P<time>[0-9.Ee+-]+)\s*$",
        group_name="time",
        log_file="{experiment_run_dir}/mvmc_zvo_CalcTimer.dat",
        units="s",
    )
