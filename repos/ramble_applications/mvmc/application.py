# Copyright 2026
# SPDX-License-Identifier: Apache-2.0

from ramble.appkit import *


class Mvmc(ExecutableApplication):
    """mVMC FermionHubbard benchmark."""

    name = "mvmc"
    tags = ["materials", "quantum", "monte-carlo", "mpi", "fugaku"]

    executable(
        "make-input",
        r"""bash -c 'mkdir -p output && (printf "%s\n" "W = {W}" "L = {L}" "Wsub = {Wsub}" "Lsub = {Lsub}" "model = {model}" "lattice = {lattice}" "t = {t}" "U = {U}" "ncond = {ncond}" "NSROptItrStep = {nsr_opt_itr_step}" "NVMCSample = {nvmc_sample}"; printf "%s%s\n" "2" "Sz = {two_sz}") > Hubbard.def'""",
        use_mpi=False,
    )

    executable(
        "run-mvmc",
        "vmc.out -s Hubbard.def",
        use_mpi=True,
    )

    executable(
        "compute-fom",
        r"""bash -c "test -s output/zvo_CalcTimer.dat && python3 -c 'import sys; get=lambda key: int(next(line.split()[-1] for line in open(sys.argv[1]) if line.split() and line.split()[0] == key)); W=get(\"W\"); L=get(\"L\"); Wsub=get(\"Wsub\"); Lsub=get(\"Lsub\"); time=float(next(line.split()[-1] for line in open(sys.argv[2]) if \"All\" in line)); work=((Lsub*Wsub)*(L*W)+(L*W))**3; print(\"mvmc_fom %.17e\nmvmc_time %.10f\nmvmc_work %.17e\" % (time/work, time, work))' Hubbard.def output/zvo_CalcTimer.dat | tee mvmc_fom.dat" """,
        use_mpi=False,
    )

    workload(
        "fermion_hubbard",
        executables=["make-input", "run-mvmc", "compute-fom"],
    )

    environment_variable(
        "OMP_NUM_THREADS",
        "{n_threads_per_proc}",
        description="Number of OpenMP threads per MPI process.",
        workloads=["fermion_hubbard"],
    )

    workload_variable(
        "W",
        default="18",
        description="Lattice width parameter.",
        workloads=["fermion_hubbard"],
    )

    workload_variable(
        "L",
        default="18",
        description="Lattice length parameter.",
        workloads=["fermion_hubbard"],
    )

    workload_variable(
        "Wsub",
        default="1",
        description="Width of the sublattice.",
        workloads=["fermion_hubbard"],
    )

    workload_variable(
        "Lsub",
        default="1",
        description="Length of the sublattice.",
        workloads=["fermion_hubbard"],
    )

    workload_variable(
        "model",
        default="FermionHubbard",
        description="mVMC model.",
        workloads=["fermion_hubbard"],
    )

    workload_variable(
        "lattice",
        default="Tetragonal",
        description="mVMC lattice type.",
        workloads=["fermion_hubbard"],
    )

    workload_variable(
        "t",
        default="1.0",
        description="Hopping parameter.",
        workloads=["fermion_hubbard"],
    )

    workload_variable(
        "U",
        default="8.0",
        description="Hubbard interaction parameter.",
        workloads=["fermion_hubbard"],
    )

    workload_variable(
        "ncond",
        default="100",
        description="mVMC ncond parameter.",
        workloads=["fermion_hubbard"],
    )

    workload_variable(
        "nsr_opt_itr_step",
        default="1",
        description="mVMC NSROptItrStep parameter.",
        workloads=["fermion_hubbard"],
    )

    workload_variable(
        "nvmc_sample",
        default="4000",
        description="mVMC NVMCSample parameter.",
        workloads=["fermion_hubbard"],
    )

    workload_variable(
        "two_sz",
        default="0",
        description="Spin-sector control parameter.",
        workloads=["fermion_hubbard"],
    )

    success_criteria(
        "mvmc-run-finished",
        mode="string",
        match=r"Exit code for run-mvmc: 0",
        file="{experiment_run_dir}/exit_codes.out",
    )

    success_criteria(
        "mvmc-fom-computed",
        mode="string",
        match=r"mvmc_fom",
        file="{experiment_run_dir}/mvmc_fom.dat",
    )

    figure_of_merit(
        "mvmc_fom",
        fom_regex=r"^mvmc_fom\s+(?P<fom>[-+0-9.Ee]+)\s*$",
        group_name="fom",
        log_file="{experiment_run_dir}/mvmc_fom.dat",
        units="s/work",
    )

    figure_of_merit(
        "mvmc_time",
        fom_regex=r"^mvmc_time\s+(?P<time>[-+0-9.Ee]+)\s*$",
        group_name="time",
        log_file="{experiment_run_dir}/mvmc_fom.dat",
        units="s",
    )

    figure_of_merit(
        "mvmc_work",
        fom_regex=r"^mvmc_work\s+(?P<work>[-+0-9.Ee]+)\s*$",
        group_name="work",
        log_file="{experiment_run_dir}/mvmc_fom.dat",
        units="work",
    )
