# Copyright 2026 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

"""Offline QWS input and application-analysis contracts; no benchmark execution."""

import ast
import importlib.util
from pathlib import Path
import sys
import types

import pytest

ROOT = Path(__file__).resolve().parents[3]
APP = ROOT / "repos/ramble_applications/qws/application.py"


@pytest.fixture
def qws(monkeypatch):
    calls = []
    kit = types.ModuleType("ramble.appkit")

    class Application:
        def add_inmem_fom_value(self, key, value):
            self.foms[key] = value

    kit.ExecutableApplication = Application
    kit.FomType = types.SimpleNamespace(TIME="time")
    kit.logger = types.SimpleNamespace(warn=lambda message: None)
    for name in (
        "executable",
        "workload",
        "workload_variable",
        "figure_of_merit",
        "success_criteria",
    ):

        def record(*args, _name=name, **kwargs):
            calls.append((_name, args, kwargs))

        setattr(kit, name, record)
    monkeypatch.setitem(sys.modules, "ramble.appkit", kit)
    spec = importlib.util.spec_from_file_location("qws_analysis_test", APP)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Qws, calls


def test_qws_selects_jacobi_with_other_solvers_present(qws):
    cls, calls = qws
    text = (
        "etime for sovler = 0.25 sec.\n"
        "LDDHMC solver with Jacobi method instead of SSOR\n"
        "etime for sovler = 2.90202498435974e+00 sec.\n"
        "LDDHMC solver with Jacobi method instead of SSOR using Half Precision\n"
        "etime for sovler = 0.5 sec.\n"
    )
    assert cls.jacobi_seconds(text) == pytest.approx(2.90202498435974)
    fom = next(call for call in calls if call[0] == "figure_of_merit")
    assert fom[1] == ("DDSolverJacobi",)
    assert fom[2]["units"] == "s"
    assert fom[2]["fom_map_key"] == "qws_jacobi_seconds"


@pytest.mark.parametrize(
    "text",
    [
        "etime for sovler = 1 sec.",
        "LDDHMC solver with Jacobi method instead of SSOR using Half Precision\netime for sovler = 1 sec.",
        (
            "LDDHMC solver with Jacobi method instead of SSOR\netime for sovler = 1 sec.\n"
        )
        * 2,
        "LDDHMC solver with Jacobi method instead of SSOR\netime for sovler = 1 sec.\netime for sovler = 2 sec.",
        "LDDHMC solver with Jacobi method instead of SSOR\netime for sovler = -1 sec.",
    ],
)
def test_qws_does_not_fallback_to_another_solver(qws, text):
    with pytest.raises(ValueError):
        qws[0].jacobi_seconds(text)


def test_qws_analysis_resets_missing_or_invalid_log(qws, tmp_path):
    cls, _ = qws
    app = cls()
    app.foms = {}
    log = tmp_path / "qws.out"
    app.expander = types.SimpleNamespace(expand_var=lambda expression: str(log))
    log.write_text(
        "LDDHMC solver with Jacobi method instead of SSOR\netime for solver = 1.5D+00 sec."
    )
    app._prepare_analysis(None)
    assert app.foms["qws_jacobi_seconds"] == 1.5
    log.unlink()
    app._prepare_analysis(None)
    assert app.foms["qws_jacobi_seconds"] is None


class _BenchparkError(Exception):
    pass


def _compute_applications_section(workload, satisfied):
    """Run Qws.compute_applications_section on a mock; return the variables."""
    tree = ast.parse((ROOT / "experiments/qws/experiment.py").read_text())
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef))
    method = next(
        node
        for node in cls.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "compute_applications_section"
    )
    namespace = {
        "BenchparkError": _BenchparkError,
        "ScalingMode": types.SimpleNamespace(
            Strong="strong", Weak="weak", Throughput="throughput"
        ),
    }
    exec(
        compile(ast.Module(body=[method], type_ignores=[]), "qws-experiment", "exec"),
        namespace,
    )
    values = {}

    def add(name, value, *args):
        if isinstance(value, dict):
            values.update(value)
        else:
            values[name] = value

    app = types.SimpleNamespace(
        workload=[workload],
        spec=types.SimpleNamespace(satisfies=lambda selection: selection in satisfied),
        add_experiment_variable=add,
        set_required_variables=lambda **kwargs: None,
        register_scaling_config=lambda value: None,
    )
    namespace["compute_applications_section"](app)
    return values


LATTICE = "lx ly lz lt px py pz pt".split()


@pytest.mark.parametrize(
    "test_mode,expected",
    [
        (True, [32, 6, 4, 3, 1, 1, 1, 1, -1, -1, 6, 50]),
        (False, [64, 12, 8, 2, 2, 2, 2, 1, -1, -1, 6, 50]),
    ],
)
def test_qws_experiment_inputs_and_perf_preservation(test_mode, expected):
    # The default workload: its lattice comes from exec_mode.
    values = _compute_applications_section(
        "qws", {"exec_mode=test"} if test_mode else set()
    )
    names = LATTICE + "tol_outer tol_inner maxiter_plus1_outer maxiter_inner".split()
    assert [int(values[name]) for name in names] == expected


@pytest.mark.parametrize("test_mode", [True, False])
def test_qws_case_workload_keeps_its_own_input(test_mode):
    # A README test case takes its lattice and process grid from the workload,
    # so the experiment must not set them, whatever the exec_mode.
    values = _compute_applications_section(
        "CASE3", {"exec_mode=test"} if test_mode else set()
    )
    assert not set(LATTICE) & set(values)
    assert values["n_ranks"] == "{n_resources}"


@pytest.mark.parametrize("scaling", ["+strong", "+weak", "+throughput"])
def test_qws_case_workload_cannot_be_scaled(scaling):
    with pytest.raises(_BenchparkError, match="workload=CASE3 is a fixed input"):
        _compute_applications_section("CASE3", {scaling})
