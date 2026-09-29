# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import shlex
import subprocess

import pytest

from benchpark.paths import paths
from benchpark.spec import SystemSpec


@pytest.mark.parametrize(
    "spec",
    [
        f"{system} compiler={compiler}"
        for system in ("riken-dgx", "riken-gh200", "riken-rikyu")
        for compiler in ("gcc", "nvhpc", "cuda")
    ]
    + [f"riken-fugaku compiler={compiler}" for compiler in ("clang", "gcc", "fj")]
    + [
        "riken-cloud cluster=fx700 compiler=fj",
        "riken-cloud cluster=genoa compiler=gcc",
        "riken-cloud cluster=gh200 compiler=nvhpc",
        "riken-cloud cluster=dgx compiler=nvhpc",
        "riken-gh200 compiler=cuda cuda=12.9 +cuda12",
        "riken-gh200 compiler=gcc gcc=15.2.0",
    ],
)
def test_riken_system_config_generation(spec, tmp_path):
    concrete = SystemSpec(spec).concretize()
    concrete.destdir = str(tmp_path)
    config = concrete.system.compute_dict()
    assert config["variables"]["variables"]["sys_cores_per_node"] > 0
    assert config["auxiliary_software_files"]["packages"]


@pytest.mark.parametrize("name", ["riken-dgx", "riken-gh200"])
def test_nvhpc_sdk_root(name):
    system = SystemSpec(f"{name} compiler=nvhpc").concretize().system
    external = system.compute_compilers_section()["packages"]["nvhpc"]["externals"][0]
    assert external["prefix"] == "/opt/nvidia/hpc_sdk"


def test_dgx_cuda_arch():
    system = SystemSpec("riken-dgx").concretize().system
    assert system.system_specific_variables()["cuda_arch"] == "121"


@pytest.mark.parametrize(
    "system_spec,experiment_spec",
    [
        ("riken-fugaku compiler=fj", "ffb"),
        ("riken-gh200 compiler=nvhpc", "ffb backend=gpu"),
        ("riken-fugaku compiler=fj", "genesis+openmp"),
        ("riken-dgx compiler=nvhpc", "genesis+cuda backend=gpu"),
        ("riken-gh200 compiler=nvhpc", "gromacs+cuda"),
        ("riken-dgx compiler=cuda", "hecbench+cuda"),
        ("riken-fugaku compiler=fj", "mvmc"),
        ("riken-fugaku compiler=fj", "qws"),
        ("riken-fugaku compiler=fj", "salmon-tddft"),
        ("riken-fugaku compiler=fj", "scale_letkf"),
    ],
)
def test_fn_experiment_config_generation(system_spec, experiment_spec, tmp_path):
    # Match normal CLI use: directives in mixins are registered at import time.
    # Load each experiment in a fresh process, not after unrelated definitions.
    system_dir = tmp_path / "system"
    benchpark = str(paths.benchpark_root / "bin" / "benchpark")
    for args in (
        ["system", "init", f"--dest={system_dir}", *shlex.split(system_spec)],
        [
            "experiment",
            "init",
            "--dest=experiment",
            str(system_dir),
            *shlex.split(experiment_spec),
        ],
    ):
        result = subprocess.run(
            [benchpark, *args], capture_output=True, text=True, timeout=120
        )
        assert result.returncode == 0, result.stdout + result.stderr
    assert (system_dir / "experiment" / "ramble.yaml").is_file()
