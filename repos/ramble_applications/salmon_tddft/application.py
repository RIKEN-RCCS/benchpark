# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import hashlib
import math
import re
from pathlib import Path

from ramble.appkit import (
    ExecutableApplication,
    FomType,
    OUTPUT_CAPTURE,
    executable,
    figure_of_merit,
    input_file,
    logger,
    success_criteria,
    tags,
    workload,
    workload_variable,
)


class SalmonTddft(ExecutableApplication):
    """SALMON GS/RT execution and final-energy checks using Ramble APIs."""

    name = "salmon-tddft"
    tags("mpi")

    # Fixed benchmark inputs and CPU reference, cross-checked on CPU/OpenACC/CUDA.
    reference = {
        "input_sha256": {
            "Si-1-1-1.nml": "867634c71d0aa21f02dec450e4d96d6201941479371095e5001ebd55e707a94a",
            "Si-1-1-1-tddft.nml": "6b2fbd65d173f753e9f0970f5a649a8ba76029b11b9b38730690114b63dca34a",
            "Si.psp8": "5fe6068c15de07c06f23e61b681855f428ec585681c4308ab4cc2249b9644c95",
            "O.psp8": "e6eab14b32e926582e778d72f4939e0c2476316209b54b458da06b2d95d9d7c2"
        },
        "absolute_energy_tolerance_eV": 1e-06,
        "absolute_time_tolerance_fs": 1e-10,
        "ground_state_iterations": 100,
        "ground_state_energy_eV": -6099.943333539265,
        "info_file": "SiO2-1x1x1_info.data",
        "rt_energy_file": "SiO2-1x1x1_rt_energy.data",
        "rt_final_time_fs": 3.0,
        "rt_final_energy_eV": -6099.81174687077
    }

    input_file(
        "benchmark-input",
        url="{salmon_input_url}",
        sha256="2bb828d9c6393bcaf4b79ba2cd0f301a0318b919df90274679ee5b5a12fad571",
        description="Benchmark inputs for SALMON",
    )

    executable(
        "pre-process",
        'rm -rf data_for_restart restart fjmpioutdir && '
        'rm -f "{salmon_gs_log}" "{salmon_rt_log}" '
        'SiO2-1x1x1_info.data SiO2-1x1x1_rt_energy.data && '
        '{preprocess} cp {input_path}/* .',
        use_mpi=False,
    )
    executable(
        "ground-state",
        "{salmon_gs_stdin_option} {salmon_executable} {salmon_gs_stdin_redirect}",
        use_mpi=True,
        redirect="{salmon_gs_log}",
        output_capture=OUTPUT_CAPTURE.ALL,
    )
    # Fujitsu MPI's -std-proc routes rank output to files, bypassing shell redirects.
    # Collect each stage before the next MPI invocation reuses those filenames.
    collect_output = (
        "if test -d fjmpioutdir; then "
        "cat fjmpioutdir/bmexe.* && rm -f fjmpioutdir/bmexe.*; fi"
    )
    executable(
        "collect-gs-output", collect_output, use_mpi=False,
        redirect="{salmon_gs_log}", output_capture=OUTPUT_CAPTURE.ALL,
    )
    executable("prepare-rt", "mv data_for_restart restart", use_mpi=False)
    executable(
        "real-time",
        "{salmon_rt_stdin_option} {salmon_executable} {salmon_rt_stdin_redirect}",
        use_mpi=True,
        redirect="{salmon_rt_log}",
        output_capture=OUTPUT_CAPTURE.ALL,
    )
    executable(
        "collect-rt-output", collect_output, use_mpi=False,
        redirect="{salmon_rt_log}", output_capture=OUTPUT_CAPTURE.ALL,
    )

    for case_name, grid_points in (
        ("Si-1-1-1", 44051),
        # ("Si-2-2-2", 346332),
        # ("Si-3-3-3", 1162035),
        # ("Si-4-4-4", 2732340),
    ):
        workload(
            case_name,
            executables=["pre-process", "ground-state", "collect-gs-output",
                         "prepare-rt", "real-time", "collect-rt-output"],
            input="benchmark-input",
        )
        for variable, default, description in (
            ("input_path", f"{{benchmark-input}}/{case_name}/input", "Benchmark inputs"),
            ("input_data_gs", f"{case_name}.nml", "Ground-state input"),
            ("input_data_rt", f"{case_name}-tddft.nml", "Real-time input"),
            ("size", str(grid_points), "Number of real-space grid points"),
            ("salmon_executable", "{salmon-tddft_path}/bin/salmon", "Spack-installed SALMON"),
            ("salmon_gs_log", "{experiment_run_dir}/salmon-gs.out", "GS output"),
            ("salmon_rt_log", "{experiment_run_dir}/salmon-rt.out", "RT output"),
            ("salmon_gs_stdin_option", "", "MPI option for GS stdin"),
            ("salmon_rt_stdin_option", "", "MPI option for RT stdin"),
            ("salmon_gs_stdin_redirect", "< {input_data_gs}", "GS stdin redirect"),
            ("salmon_rt_stdin_redirect", "< {input_data_rt}", "RT stdin redirect"),
        ):
            workload_variable(variable, default=default, description=description,
                              workload=case_name)

    number = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
    time_regex = r"^total calculation time,\s*(?P<seconds>" + number + r")\s*$"
    gs_energy_regex = r"^\s*Total energy \(eV\)\s*=\s*(?P<energy>" + number + r")\s*$"
    rt_energy_regex = r"^\s*3\.00000000\s+(?P<energy>" + number + r")\s+"

    for stage, log in (("GS", "{salmon_gs_log}"), ("RT", "{salmon_rt_log}")):
        figure_of_merit(
            f"{stage} calculation time", log_file=log, fom_regex=time_regex,
            group_name="seconds", units="s", fom_type=FomType.TIME,
        )
        success_criteria(f"{stage}-completed", mode="string",
                         match=r"^end SALMON\s*$", file=log)

    energy_criteria = {}
    for stage, log, regex, expected in (
        ("GS", "{experiment_run_dir}/SiO2-1x1x1_info.data", gs_energy_regex,
         reference["ground_state_energy_eV"]),
        ("RT", "{experiment_run_dir}/SiO2-1x1x1_rt_energy.data", rt_energy_regex,
         reference["rt_final_energy_eV"]),
    ):
        figure_of_merit(
            f"{stage} final energy", log_file=log, fom_regex=regex,
            group_name="energy", units="eV", fom_type=FomType.MEASURE,
        )
        tolerance = reference["absolute_energy_tolerance_eV"]
        energy_criteria[stage] = (
            f"({{value}} >= {expected - tolerance:.17g}) and "
            f"({{value}} <= {expected + tolerance:.17g})"
        )
        success_criteria(
            f"{stage}-energy", mode="fom_comparison", fom_name=f"{stage} final energy",
            formula=energy_criteria[stage],
        )

    figure_of_merit(
        "Figure of Merit (FOM)", fom_map_key="salmon_total_time",
        units="s", fom_type=FomType.TIME,
    )
    success_criteria("total-time-valid", mode="fom_comparison",
                     fom_name="Figure of Merit (FOM)", formula="{value} > 0")
    for stage in ("pre-process", "ground-state", "collect-gs-output", "prepare-rt",
                  "real-time", "collect-rt-output"):
        success_criteria(
            f"{stage}-exit", mode="string", match=f"^Exit code for {stage}: 0$",
            file="{experiment_run_dir}/exit_codes.out",
        )

    @classmethod
    def validate_metadata(cls, run_dir, input_files=None):
        """Check fixed input identity and completion; FOM criteria compare energies."""
        ref = cls.reference
        input_files = input_files or {}
        for name, expected in ref["input_sha256"].items():
            path = run_dir / input_files.get(name, name)
            if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                raise ValueError(f"{name}: input differs from the Si-1-1-1 reference")
        info = (run_dir / ref["info_file"]).read_text()
        count = re.search(r"Total number of iteration\s*=\s*(\d+)", info)
        if count is None or int(count[1]) != ref["ground_state_iterations"]:
            raise ValueError("Incomplete ground-state calculation")
        energy = re.search(r"Total energy \(eV\)\s*=\s*(\S+)", info)
        if energy is None or not math.isfinite(float(energy[1])):
            raise ValueError("Missing or nonfinite ground-state energy")
        last = None
        with (run_dir / ref["rt_energy_file"]).open() as stream:
            for line in stream:
                if line.strip() and not line.lstrip().startswith("#"):
                    last = line.split()
        if last is None or len(last) != 3:
            raise ValueError("Missing or malformed final RT record")
        time, energy = map(float, last[:2])
        if (not math.isfinite(time) or not math.isfinite(energy)
                or abs(time - ref["rt_final_time_fs"]) > ref["absolute_time_tolerance_fs"]):
            raise ValueError("RT did not reach a finite-energy record at 3 fs")

    @classmethod
    def stage_times(cls, run_dir, log_files):
        """Read SALMON's own timing; there is no Python or shell stopwatch."""
        result = []
        for name in log_files:
            values = re.findall(cls.time_regex, (run_dir / name).read_text(), re.MULTILINE)
            if len(values) != 1 or not math.isfinite(float(values[0])) or float(values[0]) <= 0:
                raise ValueError(f"{name}: missing or invalid SALMON timing")
            result.append(float(values[0]))
        return result

    def _prepare_analysis(self, workspace, app_inst=None):
        self.add_inmem_fom_value("salmon_total_time", None)
        try:
            run_dir = Path(self.expander.expand_var("{experiment_run_dir}"))
            logs = [self.expander.expand_var(f"{{salmon_{stage}_log}}") for stage in ("gs", "rt")]
            self.add_inmem_fom_value("salmon_total_time", sum(self.stage_times(run_dir, logs)))
        except (OSError, ValueError) as error:
            logger.warn(f"SALMON timing: {error}")

    def evaluate_success(self):
        # Ramble automatically calls this standard application success hook.
        try:
            self.validate_metadata(
                Path(self.expander.expand_var("{experiment_run_dir}")),
                input_files={
                    "Si-1-1-1.nml": self.expander.expand_var("{input_data_gs}"),
                    "Si-1-1-1-tddft.nml": self.expander.expand_var("{input_data_rt}"),
                },
            )
            return True
        except (OSError, ValueError) as error:
            logger.debug(f"SALMON input/completion check: {error}")
            return False
