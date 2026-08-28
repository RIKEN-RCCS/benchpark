# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import glob
import json
import os
import re
import shutil

import llnl.util.tty as tty

from spack.package import *
from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack_repo.builtin.build_systems.cuda import CudaPackage
from spack_repo.builtin.build_systems.rocm import ROCmPackage

# The driver that is installed into <prefix>/bin/hecbench-run.  It runs the
# whole HeCBench suite (one process, one GPU) and emits a single, uniform log
# format that the Ramble application turns into figures of merit.  It only uses
# the Python standard library so that it works in the bare experiment
# environment.
HECBENCH_RUN = r'''#!/usr/bin/env python3
"""Run the HeCBench suite and report one uniform result line per benchmark.

This driver is installed by the Benchpark/Spack `hecbench` package.  The whole
HeCBench collection is treated as *one* application: a single invocation walks
over every benchmark that has run metadata (arguments + a result regex), runs
it, extracts the benchmark's own timing metric and prints it in a fixed format.
"""

import argparse
import json
import math
import os
import re
import subprocess
import sys
import time

SELF = os.path.realpath(__file__)
BIN_DIR = os.path.dirname(SELF)
PREFIX = os.path.dirname(BIN_DIR)
DB_PATH = os.path.join(PREFIX, "share", "hecbench", "benchmarks.json")
RUNDIR_ROOT = os.path.join(PREFIX, "share", "hecbench", "rundirs")

# Ordered most specific first: microseconds must win over milliseconds, which
# must win over seconds.  The boundaries are letter-only lookarounds on purpose
# -- `\b` would not fire on "9.000ms", where the unit follows a digit.
_L = "(?<![A-Za-z])"
_R = "(?![A-Za-z])"
UNIT_PATTERNS = (
    (r"\(\s*us\s*\)", 1.0e-6),
    (r"\(\s*ms\s*\)", 1.0e-3),
    (r"\(\s*s\s*\)", 1.0),
    (r"\[\s*us\s*\]", 1.0e-6),
    (r"\[\s*ms\s*\]", 1.0e-3),
    (r"\[\s*s\s*\]", 1.0),
    (_L + r"(?:microseconds?|microsecs?|usecs?|us)" + _R, 1.0e-6),
    (_L + r"(?:milliseconds?|millisecs?|msecs?|ms)" + _R, 1.0e-3),
    (_L + r"(?:seconds?|secs?|s)" + _R, 1.0),
)


def detect_scale(text):
    """Return the multiplier that converts `text`'s unit into seconds."""
    for pattern, scale in UNIT_PATTERNS:
        if re.search(pattern, text):
            return scale
    return None


def load_db():
    with open(DB_PATH) as handle:
        return json.load(handle)


def select(db, model, selection):
    """Resolve `selection` into an ordered list of benchmark names."""
    runnable = sorted(
        name
        for name, info in db.items()
        if info.get("regex")
        and model in info.get("models", [])
        and os.path.isfile(os.path.join(BIN_DIR, model, name))
    )
    selection = (selection or "runnable").strip()
    if selection in ("", "runnable", "all", "default"):
        # `all` and `runnable` are the same set here: a benchmark without run
        # metadata has no arguments and no result regex cannot be measured even
        # if its binary was built, and a benchmark that was not built cannot be
        # run at all.
        return runnable
    if selection.startswith("category:"):
        wanted = {c.strip() for c in selection[len("category:"):].split(",") if c.strip()}
        return [n for n in runnable if wanted & set(db[n].get("categories", []))]
    names = [n.strip() for n in selection.split(",") if n.strip()]
    unknown = [n for n in names if n not in db]
    if unknown:
        sys.stderr.write("hecbench-run: unknown benchmark(s): %s\n" % ", ".join(unknown))
    return [n for n in names if n in runnable]


def run_one(name, info, model, repeat, timeout_scale):
    binary = os.path.join(BIN_DIR, model, name)
    if not os.path.isfile(binary) or not os.access(binary, os.X_OK):
        return {"status": "SKIP", "reason": "binary not built"}

    workdir = os.path.join(RUNDIR_ROOT, "%s-%s" % (name, model))
    if not os.path.isdir(workdir):
        workdir = os.path.join(RUNDIR_ROOT, "%s-cuda" % name)
    if not os.path.isdir(workdir):
        workdir = BIN_DIR

    cmd = [binary] + [str(a) for a in info.get("args", [])]
    timeout = float(info.get("timeout", 300)) * timeout_scale
    pattern = re.compile(info["regex"])

    best_metric = None
    best_scale = None
    walltime = 0.0
    status = "FAIL"
    reason = ""
    output = ""
    for _ in range(max(1, repeat)):
        start = time.time()
        try:
            proc = subprocess.run(
                cmd,
                cwd=workdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            walltime += time.time() - start
            status, reason = "TIMEOUT", "exceeded %.0fs" % timeout
            break
        except OSError as err:
            status, reason = "FAIL", str(err)
            break
        walltime += time.time() - start
        output = proc.stdout.decode("utf-8", "replace")
        if proc.returncode != 0:
            status, reason = "FAIL", "exit code %d" % proc.returncode
            break
        match = pattern.search(output)
        if not match:
            status, reason = "FAIL", "result pattern not found"
            break
        try:
            metric = float(match.group(1))
        except (IndexError, ValueError):
            status, reason = "FAIL", "result is not a number"
            break
        status, reason = "PASS", ""
        scale = detect_scale(match.group(0))
        if best_metric is None or metric < best_metric:
            best_metric, best_scale = metric, scale

    result = {
        "status": status,
        "reason": reason,
        "walltime": walltime,
        "metric": best_metric,
        "kernel_time": None if (best_metric is None or best_scale is None)
        else best_metric * best_scale,
    }
    if status != "PASS":
        result["tail"] = output[-400:]
    return result


def main():
    parser = argparse.ArgumentParser(description="Run the HeCBench suite")
    parser.add_argument("--model", default="cuda",
                        help="programming model: cuda, hip, sycl or omp")
    parser.add_argument("--select", default="runnable",
                        help="'runnable', 'category:<c1,c2>' or a comma separated "
                             "list of benchmark names")
    parser.add_argument("--repeat", type=int, default=1,
                        help="runs per benchmark; the best metric is reported")
    parser.add_argument("--timeout-scale", type=float, default=1.0,
                        help="multiplier applied to each benchmark's timeout")
    parser.add_argument("--results", default="hecbench-results.json",
                        help="machine readable results file to write")
    args = parser.parse_args()

    db = load_db()
    names = select(db, args.model, args.select)

    print("### HeCBench run")
    print("HeCBench prefix: %s" % PREFIX)
    print("HeCBench model: %s" % args.model)
    print("HeCBench selection: %s" % args.select)
    print("HeCBench benchmarks selected: %d" % len(names))
    sys.stdout.flush()

    results = {}
    started = time.time()
    for name in names:
        info = db[name]
        res = run_one(name, info, args.model, args.repeat, args.timeout_scale)
        results[name] = res
        metric = "NA" if res.get("metric") is None else "%.6e" % res["metric"]
        ktime = "NA" if res.get("kernel_time") is None else "%.6e" % res["kernel_time"]
        print("[hecbench] benchmark=%s model=%s status=%s metric=%s kernel_time=%s "
              "walltime=%.3f" % (name, args.model, res["status"], metric, ktime,
                                 res.get("walltime", 0.0)))
        if res["status"] != "PASS":
            print("[hecbench]   reason: %s" % res.get("reason", ""))
        sys.stdout.flush()
    elapsed = time.time() - started

    passed = [n for n, r in results.items() if r["status"] == "PASS"]
    failed = [n for n, r in results.items() if r["status"] in ("FAIL", "TIMEOUT")]
    skipped = [n for n, r in results.items() if r["status"] == "SKIP"]
    timings = [results[n]["kernel_time"] for n in passed
               if results[n]["kernel_time"] not in (None, 0.0)]
    attempted = len(passed) + len(failed)
    pass_rate = 100.0 * len(passed) / attempted if attempted else 0.0
    geomean = (math.exp(sum(math.log(t) for t in timings) / len(timings))
               if timings else float("nan"))
    total_kernel = sum(timings) if timings else 0.0

    print("")
    print("### HeCBench summary")
    print("HeCBench model: %s" % args.model)
    print("HeCBench benchmarks attempted: %d" % attempted)
    print("HeCBench benchmarks passed: %d" % len(passed))
    print("HeCBench benchmarks failed: %d" % len(failed))
    print("HeCBench benchmarks skipped: %d" % len(skipped))
    print("HeCBench pass rate: %.2f %%" % pass_rate)
    print("HeCBench total kernel time: %.6e s" % total_kernel)
    print("HeCBench geometric mean kernel time: %.6e s" % geomean)
    print("HeCBench suite walltime: %.3f s" % elapsed)
    print("HeCBench throughput: %.4f benchmarks/s"
          % (len(passed) / elapsed if elapsed > 0 else 0.0))
    if failed:
        print("HeCBench failing benchmarks: %s" % " ".join(sorted(failed)))
    if skipped:
        print("HeCBench skipped benchmarks: %s" % " ".join(sorted(skipped)))
    print("HeCBench status: %s" % ("OK" if passed and not failed else
                                   ("DEGRADED" if passed else "FAILED")))

    try:
        with open(args.results, "w") as handle:
            json.dump({"model": args.model, "selection": args.select,
                       "elapsed": elapsed, "results": results}, handle, indent=1)
    except OSError as err:
        sys.stderr.write("hecbench-run: could not write results: %s\n" % err)

    # The suite as a whole succeeds when at least one benchmark produced a
    # figure of merit; per-benchmark failures are reported, not fatal.
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
'''

# Files that are never needed in a benchmark's run directory.
_SOURCE_SUFFIXES = (
    ".c", ".cc", ".cpp", ".cu", ".cuh", ".cxx", ".h", ".hpp", ".hip", ".o",
)


class Hecbench(CMakePackage, CudaPackage, ROCmPackage):
    """HeCBench is a collection of heterogeneous computing benchmarks written
    in CUDA, HIP, SYCL and OpenMP target offloading, used to study performance,
    portability and productivity across GPU programming models.

    Benchpark treats the whole collection as a single application: one Spack
    install builds every benchmark of the selected programming model, and one
    run of `hecbench-run` executes the suite and reports a figure of merit per
    benchmark plus suite-level aggregates.
    """

    tags = ["benchmark"]
    homepage = "https://github.com/RIKEN-RCCS/HeCBench"
    git = "https://github.com/RIKEN-RCCS/HeCBench.git"

    maintainers("ando")

    license("BSD-3-Clause")

    version("master", branch="master")
    version("2026.08.16", commit="06d24631a6f977ba8d3ba053073471ac9bd77b7a")

    variant(
        "openmp",
        default=False,
        description="Build the OpenMP target-offload flavour of the benchmarks",
    )
    variant(
        "sycl",
        default=False,
        description="Build the SYCL flavour of the benchmarks",
    )
    variant(
        "benchmarks",
        default="runnable",
        values=("smoke", "runnable", "all"),
        multi=False,
        description="Which part of the suite to build: 'smoke' for a small "
        "representative set, 'runnable' for every benchmark Benchpark can "
        "measure (those with run arguments and a result pattern), or 'all' for "
        "every benchmark of the selected programming model",
    )

    requires(
        "+cuda",
        "+rocm",
        "+sycl",
        "+openmp",
        policy="one_of",
        msg="exactly one HeCBench programming model must be selected: "
        "+cuda, +rocm (HIP), +sycl or +openmp (target offload)",
    )

    depends_on("c", type="build")
    depends_on("cxx", type="build")
    # a few benchmarks (axhelm, ccsd-trpdrv, ...) enable the Fortran language
    depends_on("fortran", type="build")
    depends_on("cmake@3.21:", type="build")
    depends_on("cuda", when="+cuda")

    @property
    def model(self):
        """HeCBench's name for the selected programming model."""
        if self.spec.satisfies("+cuda"):
            return "cuda"
        if self.spec.satisfies("+rocm"):
            return "hip"
        if self.spec.satisfies("+sycl"):
            return "sycl"
        return "omp"

    def metadata(self):
        """Parse HeCBench's benchmarks.yaml into a plain dictionary.

        Only the handful of keys Benchpark needs is extracted, so a tiny line
        oriented parser is enough and no YAML module is required at build time.
        """
        path = join_path(self.stage.source_path, "benchmarks.yaml")
        entries = {}
        current = None
        section = None
        with open(path) as handle:
            for line in handle:
                line = line.rstrip("\n")
                if not line.strip() or line.lstrip().startswith("#"):
                    continue
                indent = len(line) - len(line.lstrip())
                text = line.strip()
                if indent == 0 and text.endswith(":"):
                    current = text[:-1].strip()
                    section = None
                    entries[current] = {"categories": [], "models": []}
                    continue
                if current is None:
                    continue
                key, _, value = text.partition(":")
                key, value = key.strip(), value.strip()
                if indent == 2:
                    section = key if key == "test" else None
                    if key in ("categories", "models"):
                        entries[current][key] = [
                            v.strip() for v in value.strip("[]").split(",") if v.strip()
                        ]
                elif indent >= 4 and section == "test":
                    if key == "regex":
                        entries[current]["regex"] = value.strip("'\"")
                    elif key == "args":
                        entries[current]["args"] = [
                            v.strip().strip("'\"")
                            for v in value.strip("[]").split(",")
                            if v.strip()
                        ]
                    elif key == "timeout":
                        entries[current]["timeout"] = int(value)
        return entries

    def runnable_benchmarks(self):
        """Benchmarks that have run arguments, a result pattern and sources."""
        model = self.model
        names = []
        for name, info in sorted(self.metadata().items()):
            if not info.get("regex") or model not in info.get("models", []):
                continue
            bench_dir = join_path(self.stage.source_path, "src", f"{name}-{model}")
            if not os.path.isfile(join_path(bench_dir, "CMakeLists.txt")):
                continue
            if self.benchmark_is_buildable(name, model):
                names.append(name)
        return names

    #: Keywords that terminate the SOURCES list of add_hecbench_benchmark()
    _CMAKE_KEYWORDS = frozenset(
        (
            "NAME", "MODEL", "SOURCES", "CATEGORIES", "COMPILE_OPTIONS",
            "LINK_LIBRARIES", "INCLUDE_DIRS", "TEST_REGEX", "TEST_ARGS",
            "TEST_TIMEOUT", "ENABLE_FASTMATH",
        )
    )

    def benchmark_is_buildable(self, name, model):
        """Can `<name>-<model>` be configured with the sources on disk?

        HeCBench keeps some benchmark inputs (and even a few source archives)
        in DVC, which needs S3 credentials to pull, and a handful of its
        CMakeLists.txt files name sources that are not in the repository. Those
        benchmarks abort the whole CMake configure, so they are detected here
        and dropped from the build.
        """
        bench_dir = join_path(self.stage.source_path, "src", f"{name}-{model}")
        cmakelists = join_path(bench_dir, "CMakeLists.txt")
        if not os.path.isfile(cmakelists):
            # Nothing is registered for this model, CMake simply skips it.
            return True

        # DVC-managed content that was never pulled.
        for pointer in glob.glob(join_path(bench_dir, "*.dvc")):
            if not os.path.exists(pointer[: -len(".dvc")]):
                return False
        for entry in os.listdir(bench_dir):
            path = join_path(bench_dir, entry)
            if os.path.islink(path) and not os.path.exists(path):
                return False

        # Sources the benchmark declares but does not ship.
        with open(cmakelists) as handle:
            content = handle.read()
        for block in re.findall(
            r"add_hecbench_benchmark\s*\((.*?)\)", content, re.S
        ):
            tokens = block.split()
            if "SOURCES" not in tokens:
                continue
            for token in tokens[tokens.index("SOURCES") + 1:]:
                if token in self._CMAKE_KEYWORDS:
                    break
                if "$" in token or "{" in token:
                    continue
                if not os.path.isfile(join_path(bench_dir, token)):
                    return False
        return True

    @run_before("cmake")
    def prune_unbuildable_benchmarks(self):
        """Drop benchmarks that cannot be configured from HeCBench's own list.

        `src/CMakeLists.txt` enumerates every benchmark it adds; a single
        unbuildable entry fails the configure step for the whole suite, so the
        list is rewritten to contain only what this checkout can actually
        build.
        """
        src_cmakelists = join_path(self.stage.source_path, "src", "CMakeLists.txt")
        with open(src_cmakelists) as handle:
            content = handle.read()

        match = re.search(
            r"set\(HECBENCH_POC_BENCHMARKS(?P<body>.*?)\n\)", content, re.S
        )
        if not match:
            tty.warn("hecbench: benchmark list not found, nothing pruned")
            return

        model = self.model
        keep, dropped = [], []
        for line in match.group("body").splitlines():
            name = line.split("#")[0].strip()
            if not name:
                continue
            (keep if self.benchmark_is_buildable(name, model) else dropped).append(name)

        if not dropped:
            return

        body = "\n" + "\n".join(f"    {name}" for name in keep) + "\n"
        content = content[: match.start("body")] + body + content[match.end("body"):]
        with open(src_cmakelists, "w") as handle:
            handle.write(content)
        tty.msg(
            f"hecbench: skipping {len(dropped)} benchmark(s) whose sources or "
            f"inputs are missing from this checkout: {' '.join(sorted(dropped))}"
        )

    #: A small, fast and self-contained cross section of the suite, used to
    #: validate an installation without building several hundred kernels.
    smoke_benchmarks = (
        "accuracy",
        "ace",
        "adam",
        "aobench",
        "bilateral",
        "bitonic-sort",
        "fft",
        "jacobi",
        "mandelbrot",
        "matrix-rotate",
        "nbody",
        "softmax",
    )

    def selected_benchmarks(self):
        """Benchmarks whose binaries this install should produce."""
        runnable = self.runnable_benchmarks()
        if self.spec.satisfies("benchmarks=smoke"):
            return [n for n in runnable if n in self.smoke_benchmarks]
        return runnable

    @property
    def build_targets(self):
        # `benchmarks=all` builds CMake's default target, i.e. everything that
        # HeCBench registers for the selected programming model.
        if self.spec.satisfies("benchmarks=all"):
            return []
        return [f"{name}-{self.model}" for name in self.selected_benchmarks()]

    def _compiler_basename(self):
        """Name of the C++ compiler Spack wraps for this build, if known."""
        cxx = globals().get("spack_cxx")
        if not cxx:
            return ""
        try:
            return os.path.basename(os.path.realpath(cxx))
        except OSError:
            return os.path.basename(cxx)

    def _compiler_is_nvcc(self):
        """True when Spack picked nvcc itself as this build's C++ compiler.

        Some systems (Benchpark's `compiler=cuda` for instance) register the
        CUDA toolkit as a c/cxx provider.  CMake cannot drive a C++ project with
        nvcc as CMAKE_CXX_COMPILER, so this is detected and worked around.
        """
        if self._compiler_basename().startswith("nvcc"):
            return True
        try:
            return self.spec["cxx"].name == "cuda"
        except KeyError:
            return False

    @staticmethod
    def _nvhpc_math_libs(cuda_prefix):
        """Locate the CUDA math libraries of an NVIDIA HPC SDK installation.

        The HPC SDK ships the CUDA toolkit as `<sdk>/cuda/<x.y>` but keeps
        cuBLAS, cuFFT, cuSOLVER and friends in a sibling `<sdk>/math_libs/<x.y>`
        tree, so a plain CUDAToolkit_ROOT does not expose their headers.
        """
        cuda_prefix = str(cuda_prefix).rstrip("/")
        sdk_root, _, version = cuda_prefix.rpartition("/")
        sdk_root, _, cuda_dir = sdk_root.rpartition("/")
        if cuda_dir != "cuda":
            return None
        candidate = os.path.join(sdk_root, "math_libs", version)
        if os.path.isfile(os.path.join(candidate, "include", "cublas_v2.h")):
            return candidate
        return None

    def cmake_args(self):
        spec = self.spec
        model = self.model
        args = [
            self.define("HECBENCH_ENABLE_CUDA", model == "cuda"),
            self.define("HECBENCH_ENABLE_HIP", model == "hip"),
            self.define("HECBENCH_ENABLE_SYCL", model == "sycl"),
            self.define("HECBENCH_ENABLE_OPENMP", model == "omp"),
            # Benchpark drives the runs itself, so CTest registration (which
            # would pull in a Python3 requirement) is not needed.
            self.define("HECBENCH_ENABLE_TESTING", False),
            self.define("HECBENCH_BUILD_ALL_BENCHMARKS", True),
        ]

        if model == "cuda":
            cuda_arch = spec.variants["cuda_arch"].value
            if cuda_arch and cuda_arch[0] != "none":
                args.append(self.define("HECBENCH_CUDA_ARCH", cuda_arch[0]))
            args.append(self.define("CUDAToolkit_ROOT", spec["cuda"].prefix))
            args.append(
                self.define("CMAKE_CUDA_COMPILER", spec["cuda"].prefix.bin.nvcc)
            )

            math_libs = self._nvhpc_math_libs(spec["cuda"].prefix)
            if math_libs:
                tty.msg(f"hecbench: using CUDA math libraries from {math_libs}")
                include = os.path.join(math_libs, "include")
                lib = os.path.join(math_libs, "lib64")
                args.append(self.define("CMAKE_CUDA_FLAGS", f"-I{include}"))
                args.append(self.define("CMAKE_CXX_FLAGS", f"-I{include}"))
                args.append(
                    self.define(
                        "CMAKE_EXE_LINKER_FLAGS", f"-L{lib} -Wl,-rpath,{lib}"
                    )
                )
            # CMake cannot use nvcc as the C/C++ compiler for the host code, so
            # fall back to a real host compiler when the Benchpark system
            # selected `compiler=cuda` (whose c/cxx entries are nvcc).
            if self._compiler_is_nvcc():
                host_cc, host_cxx = which("gcc"), which("g++")
                if not host_cxx:
                    raise InstallError(
                        "hecbench needs a host C++ compiler next to nvcc; "
                        "none was found on PATH"
                    )
                if host_cc:
                    args.append(self.define("CMAKE_C_COMPILER", host_cc.path))
                args.append(self.define("CMAKE_CXX_COMPILER", host_cxx.path))
                args.append(self.define("CMAKE_CUDA_HOST_COMPILER", host_cxx.path))

        elif model == "hip":
            amdgpu_target = spec.variants["amdgpu_target"].value
            if amdgpu_target and amdgpu_target[0] != "none":
                args.append(self.define("HECBENCH_HIP_ARCH", amdgpu_target[0]))

        elif model == "omp":
            # nvhpc and amdclang need different offload flags; pick them from
            # the compiler that Spack selected for this build.
            if self._compiler_basename().startswith("nvc"):
                cuda_arch = spec.variants["cuda_arch"].value
                arch = cuda_arch[0] if cuda_arch and cuda_arch[0] != "none" else "80"
                args.append(self.define("HECBENCH_OMP_TARGET", "-mp=gpu"))
                args.append(self.define("HECBENCH_OMP_TARGET_BACKEND", f"-gpu=cc{arch}"))
                args.append(self.define("HECBENCH_OMP_FASTMATH", "-gpu=fastmath"))
            else:
                args.append(self.define("HECBENCH_OMP_TARGET", "-fopenmp"))

        return args

    def build(self, spec, prefix):
        """Build the selected benchmarks, tolerating individual failures.

        HeCBench is a collection of independent programs, and in any given
        environment a few of them will not compile (a missing optional library,
        an upstream bug, an unsupported intrinsic).  `make -k` keeps going so
        that one broken kernel does not cost the whole suite; whatever was
        produced is installed, and `hecbench-run` reports anything missing.
        """
        with working_dir(self.build_directory):
            try:
                make("-k", *self.build_targets)
            except ProcessError:
                tty.warn(
                    "hecbench: some benchmarks did not compile; continuing with "
                    "the ones that did"
                )

    def install(self, spec, prefix):
        """Install the benchmark binaries, their run directories and the driver.

        HeCBench's CMake project has no install rules of its own -- it does not
        even generate an `install` target -- and leaves the binaries in
        <build>/bin/<model>.  They are copied here together with each runnable
        benchmark's source directory, which is what the upstream CTest harness
        uses as the working directory (a few benchmarks read input files from
        there).
        """
        model = self.model

        built = join_path(self.build_directory, "bin", model)
        mkdirp(join_path(prefix.bin, model))
        installed = []
        if os.path.isdir(built):
            for entry in sorted(os.listdir(built)):
                source = join_path(built, entry)
                if os.path.isfile(source) and os.access(source, os.X_OK):
                    # NOTE: shutil, not Spack's install(), which this method
                    # shadows. copy2 keeps the executable bit.
                    shutil.copy2(source, join_path(prefix.bin, model, entry))
                    installed.append(entry)
        if not installed:
            raise InstallError(f"no HeCBench {model} binaries were produced")
        tty.msg(f"hecbench: installed {len(installed)} {model} benchmark binaries")

        missing = sorted(set(self.selected_benchmarks()) - set(installed))
        if missing:
            tty.warn(
                f"hecbench: {len(missing)} selected benchmark(s) did not build: "
                f"{' '.join(missing)}"
            )

        metadata = self.metadata()
        rundirs = join_path(prefix.share, "hecbench", "rundirs")
        mkdirp(rundirs)
        for name in self.runnable_benchmarks():
            source = join_path(self.stage.source_path, "src", f"{name}-{model}")
            target = join_path(rundirs, f"{name}-{model}")
            self._copy_rundir(source, target)

        db_path = join_path(prefix.share, "hecbench", "benchmarks.json")
        with open(db_path, "w") as handle:
            json.dump(metadata, handle, indent=1, sort_keys=True)

        driver = join_path(prefix.bin, "hecbench-run")
        with open(driver, "w") as handle:
            handle.write(HECBENCH_RUN)
        os.chmod(driver, 0o755)

    def _copy_rundir(self, source, target):
        """Copy a benchmark's data files, skipping sources and dead symlinks."""
        if not os.path.isdir(source):
            return
        mkdirp(target)
        for root, dirs, files in os.walk(source):
            dirs[:] = [d for d in dirs if d not in (".git", "build")]
            rel = os.path.relpath(root, source)
            dest_root = target if rel == "." else join_path(target, rel)
            mkdirp(dest_root)
            for name in files:
                if name.endswith(_SOURCE_SUFFIXES) or name in (
                    "CMakeLists.txt",
                    "Makefile",
                ):
                    continue
                path = join_path(root, name)
                if not os.path.exists(path):
                    # dvc-managed input that was never pulled
                    continue
                try:
                    shutil.copy2(path, join_path(dest_root, name))
                except (OSError, shutil.Error):
                    continue
