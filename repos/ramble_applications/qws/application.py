# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import math
import re
from pathlib import Path

from ramble.appkit import *


class Qws(ExecutableApplication):
    """QWS benchmark for Lattice quantum chromodynamics simulation library for
    Fugaku and computers with wide SIMD
    """
    name = "QWS"

    tags = ['qcd','c++','mpi', 'weak-scaling']

    executable('qws', 'qws.exe' +
                      ' {lx} {ly} {lz} {lt}' +
                      ' {px} {py} {pz} {pt}' +
                      ' {tol_outer} {tol_inner}' +
                      ' {maxiter_plus1_outer} {maxiter_inner}', use_mpi=True)

    workload('qws', executables=['qws'])

    workload_variable('lx', default='32',
                      description='Dimension of the rank-local lattice in X. (Default: 32)',
                      workloads=['qws'])
    workload_variable('ly', default='6',
                      description='Dimension of the rank-local lattice in Y. (Default: 6)',
                      workloads=['qws'])
    workload_variable('lz', default='4',
                      description='Dimension of the rank-local lattice in Z. (Default: 4)',
                      workloads=['qws'])
    workload_variable('lt', default='3',
                      description='Dimension of the rank-local lattice in T. (Default: 3)',
                      workloads=['qws'])
    workload_variable('px', default='1',
                      description='Scale lattice in X dimension by number of ranks. (Default: 1)',
                      workloads=['qws'])
    workload_variable('py', default='1',
                      description='Scale lattice in Y dimension by number of ranks. (Default: 1)',
                      workloads=['qws'])
    workload_variable('pz', default='1',
                      description='Scale lattice in Z dimension by number of ranks. (Default: 1)',
                      workloads=['qws'])
    workload_variable('pt', default='1',
                      description='Scale lattice in T dimension by number of ranks. (Default: 1)',
                      workloads=['qws'])
    workload_variable('tol_outer', default='-1',
                      description='Tolerance of outer DD solver of BiCGStab. (Default: -1)',
                      workloads=['qws'])
    workload_variable('tol_inner', default='-1',
                      description='Tolerance of inner DD solver of BiCGStab. (Default: -1)',
                      workloads=['qws'])
    workload_variable('maxiter_plus1_outer', default='6',
                      description='Maximum iterations of outer DD solver. (Default: 6)',
                      workloads=['qws'])
    workload_variable('maxiter_inner', default='50',
                      description='Maximum iterations of inner DD solver. (Default: 50)',
                      workloads=['qws'])

    # The test cases listed in QWS's README, one workload each, so that the
    # workload name says which input was run. Values are the rank-local
    # lattice (lx ly lz lt) and the process grid (px py pz pt); every case
    # uses tolerances -1 -1, 6 outer and 50 inner iterations.
    _cases = {
        'CASE0': (32, 6, 4, 3, 1, 1, 1, 1),
        'CASE1': (32, 6, 4, 3, 1, 1, 1, 2),
        'CASE2': (32, 3, 4, 4, 1, 1, 1, 2),
        'CASE3': (32, 3, 6, 4, 1, 1, 1, 2),
        'CASE4': (32, 6, 6, 2, 1, 1, 1, 2),
        'CASE5': (32, 6, 6, 4, 1, 1, 1, 2),
        'CASE6': (32, 6, 6, 8, 1, 1, 1, 2),
        'CASE7': (32, 6, 4, 3, 1, 2, 2, 2),
        'CASE8': (32, 6, 4, 3, 4, 4, 1, 1),
        'CASE9': (32, 6, 4, 3, 1, 1, 4, 4),
    }
    for _case in _cases:
        workload(_case, executables=['qws'])
    for _i, _var in enumerate(['lx', 'ly', 'lz', 'lt', 'px', 'py', 'pz', 'pt']):
        _defaults = {}
        for _case, _values in _cases.items():
            _defaults[_case] = str(_values[_i])
        workload_variable(_var, workload_defaults=_defaults)
    for _var, _value in (('tol_outer', '-1'), ('tol_inner', '-1'),
                         ('maxiter_plus1_outer', '6'), ('maxiter_inner', '50')):
        workload_variable(_var, default=_value, workloads=list(_cases))
    del _cases, _case, _i, _var, _defaults, _values, _value

    # This interval surrounds bicgstab_dd_mix_ and its trailing MPI barrier,
    # excluding initialization and the subsequent residual validation.
    figure_of_merit(
        "DDSolverJacobi",
        fom_map_key="qws_jacobi_seconds",
        units="s",
        fom_type=FomType.TIME,
    )
    success_criteria(
        "jacobi-time-valid",
        mode="fom_comparison",
        fom_name="DDSolverJacobi",
        formula="{value} >= 0",
    )

    @staticmethod
    def jacobi_seconds(text):
        """Select the named Jacobi interval, never the first or last solver."""
        heading = "LDDHMC solver with Jacobi method instead of SSOR"
        timing = re.compile(
            r"^etime for so(?:vl|lv)er\s*=\s*"
            r"([-+]?[0-9]+(?:\.[0-9]*)?(?:[eEdD][-+]?[0-9]+)?)\s+sec\.\s*$"
        )
        active = False
        headings = 0
        values = []
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("LDDHMC solver"):
                active = line == heading
                headings += active
            match = timing.fullmatch(line)
            if active and match:
                value = float(match[1].replace("D", "e").replace("d", "e"))
                if not math.isfinite(value) or value < 0:
                    raise ValueError("Invalid QWS Jacobi timing")
                values.append(value)
        if headings != 1 or len(values) != 1:
            raise ValueError("Missing or ambiguous QWS Jacobi interval")
        return values[0]

    def _prepare_analysis(self, workspace, app_inst=None):
        self.add_inmem_fom_value("qws_jacobi_seconds", None)
        try:
            log = Path(
                self.expander.expand_var("{experiment_run_dir}/{experiment_name}.out")
            )
            self.add_inmem_fom_value(
                "qws_jacobi_seconds", self.jacobi_seconds(log.read_text())
            )
        except (OSError, UnicodeError, ValueError) as error:
            logger.warn(f"QWS Jacobi timing: {error}")
