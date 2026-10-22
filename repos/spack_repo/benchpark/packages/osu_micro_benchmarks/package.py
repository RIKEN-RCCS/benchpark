# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import os

from spack.package import *
from spack_repo.builtin.build_systems.rocm import ROCmPackage
from spack_repo.builtin.packages.osu_micro_benchmarks.package import (
    OsuMicroBenchmarks as BuiltinOsu,
)


class OsuMicroBenchmarks(BuiltinOsu, ROCmPackage):

    # `-P <events>:<file>` records PAPI counters during a run. OMB 7.5.x takes
    # the option in its plain MPI builds only; these two patches (RIKEN R-CCS)
    # make the accelerator builds take it as well.
    patch("add-papi-option.patch", when="@7.5:7.5.2 +papi")
    patch("add-papi-osu_util.patch", when="@7.5:7.5.2 +papi")

    # configure builds the osu_oshm_* benchmarks when the compiler it is
    # given links an OpenSHMEM library, so this hands it the MPI's oshcc
    # (HPC-X and Open MPI with OSHMEM ship one) in place of mpicc.
    variant(
        "openshmem",
        default=False,
        description="Build the OpenSHMEM benchmarks with the MPI's oshcc",
    )

    depends_on("cray-mpich+gtl", when="+rocm")

    def configure_args(self):
        args = super().configure_args()
        if self.spec.satisfies("+rocm"):
            if "--enable-rocm" not in args:
                args.append("--enable-rocm")
            args.extend([f"LDFLAGS={self.spec['mpi'].libs.ld_flags}"])
            print(self.spec['mpi'])
        if self.spec.satisfies("+cuda") and self.spec.satisfies("%nvhpc"):
            # nvcc takes the C++ compiler as its host compiler, and with
            # nvc++ (nvhpc 26.9, CUDA 13.3) OMB's kernel.cu stops on
            # `type "__pgi_va_list_helper" has already been defined` in
            # nvhpc's own _cplus_nvcc.h. Hand nvcc the system's g++ instead;
            # the kernels are plain CUDA C and link with the nvc-built rest.
            gxx = "/usr/bin/g++" if os.path.exists("/usr/bin/g++") else which("g++")
            if gxx:
                args = [
                    f"{a} -ccbin {gxx}" if a.startswith("NVCCFLAGS=") else a for a in args
                ]
                if not any(a.startswith("NVCCFLAGS=") for a in args):
                    args.append(f"NVCCFLAGS=-ccbin {gxx}")
        if self.spec.satisfies("+openshmem"):
            oshcc = join_path(self.spec["mpi"].prefix.bin, "oshcc")
            oshcxx = join_path(self.spec["mpi"].prefix.bin, "oshc++")
            if not os.path.exists(oshcc):
                raise InstallError(
                    f"+openshmem: {oshcc} does not exist; this MPI has no OpenSHMEM compiler"
                )
            args = [a for a in args if not a.startswith(("CC=", "CXX="))]
            args.extend([f"CC={oshcc}", f"CXX={oshcxx}"])
        new_args = list()
        for x in args:
            if "NVCCFLAGS" in x and self.spec.satisfies("%intel-oneapi-compilers"):
                new_args.append(x + " -allow-unsupported-compiler")
            else:
                new_args.append(x)
        return new_args

    def setup_run_environment(self, env):
        mpidir = join_path(self.prefix.libexec, "osu-micro-benchmarks", "mpi")
        env.prepend_path("PATH", join_path(mpidir, "startup"))
        env.prepend_path("PATH", join_path(mpidir, "pt2pt"))
        env.prepend_path("PATH", join_path(mpidir, "one-sided"))
        env.prepend_path("PATH", join_path(mpidir, "collective"))
        env.prepend_path("PATH", join_path(mpidir, "congestion"))
        env.prepend_path("PATH", join_path(mpidir, "pt2pt", "persistent"))
        if self.spec.satisfies("+rocm"):
            if 'gtl_flags' in self.spec['mpi'].extra_attributes:
                env.prepend_path("LOCAL_RANK", self.spec['mpi'].extra_attributes['gtl_flags'])
        if self.spec.satisfies("+xccl"):
            xccldir = join_path(self.prefix.libexec, "osu-micro-benchmarks", "xccl")
            env.prepend_path("PATH", join_path(xccldir, "pt2pt"))
            env.prepend_path("PATH", join_path(xccldir, "collective"))
        if self.spec.satisfies("+openshmem"):
            env.prepend_path(
                "PATH", join_path(self.prefix.libexec, "osu-micro-benchmarks", "openshmem")
            )
