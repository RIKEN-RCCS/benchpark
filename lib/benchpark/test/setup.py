# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from types import SimpleNamespace

import pytest
import yaml

import benchpark.cmd.setup as setup


@pytest.mark.parametrize("package_manager", ["spack", "user-managed"])
def test_setup_without_managed_spack(tmp_path, monkeypatch, package_manager):
    """External Spack and user-managed packages need no site mirror command."""
    system_dir = tmp_path / "system"
    experiment_dir = tmp_path / "experiment"
    system_dir.mkdir()
    experiment_dir.mkdir()
    (experiment_dir / "ramble.yaml").write_text(
        yaml.safe_dump({"package_manager": package_manager, "destdir": str(system_dir)})
    )
    monkeypatch.setattr(setup, "determine_experiment_id", lambda _: "test/experiment")
    monkeypatch.setattr(
        setup.RuntimeResources,
        "ramble_first_time_setup",
        lambda self: (None, False),
    )
    external_spack = tmp_path / "external-spack"
    external_spack.mkdir()
    workspace = tmp_path / "workspace"
    args = SimpleNamespace(
        experiment=experiment_dir,
        experiments_root=workspace,
        spack=str(external_spack) if package_manager == "spack" else None,
        environment=None,
    )

    setup.command(args)

    initializer = (workspace / "setup.sh").read_text()
    assert "ramble/setup-env.sh" in initializer
    assert "mirror.sh" not in initializer
    if package_manager == "spack":
        assert (workspace / "spack").resolve() == external_spack
        assert "spack/setup-env.sh" in initializer
    else:
        assert "spack/setup-env.sh" not in initializer
