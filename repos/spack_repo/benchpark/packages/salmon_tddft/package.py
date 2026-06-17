# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import os

from spack.package import *
from spack_repo.builtin.build_systems.cmake import CMakePackage


class SalmonTddft(CMakePackage):
    """SALMON is an open-source computer program for ab-initio quantum-mechanical 
    calculations of electron dynamics at the nanoscale that takes place in 
    various situations of light-matter interactions. 
    It is based on time-dependent density functional theory, solving time-dependent 
    Kohn-Sham equation in real time and real space with norm-conserving pseudopotentials."""

    homepage = "https://salmon-tddft.jp/"
    git      = "https://github.com/SALMON-TDDFT/SALMON2"

    license("BSD-3-Clause-Open-MPI")

    version('2.2.2', tag='v.2.2.2')
    version('2.2.1', tag='v.2.2.1')
    version('2.2.0', tag='v.2.2.0')
    version('2.1.0', tag='v.2.1.0')
    version('2.0.2', tag='v.2.0.2')
    version('2.0.1', tag='v.2.0.1')
    version('2.0.0', tag='v.2.0.0')

    depends_on("c", type="build")
    depends_on("fortran", type="build")

    variant("build_type", default="Release", values=("Release", "Debug"))
    variant("openmp", default=True, description="Enable OpenMP")
    variant("libxc", default=False, description="Enable libxc")
    variant("scalapack", default=False, description="Enable scalapack")
    variant("eigenexa", default=False, description="Enable eigenexa")
    variant("cuda", default=False, description="Enable cuda")
    variant("rocm", default=False, description="Enable rocm")

    depends_on("cmake@3.14:", type="build")
    depends_on("scalapack", type="link", when="+scalapack")
    depends_on("eigenexa", type="link", when="+eigenexa")
    depends_on("libxc", type="link", when="+libxc")
    depends_on("lapack", type="link", when="%gcc")

    conflicts("+eigenexa", when="~scalapack")

    if 'cloud.r-ccs.riken.jp' in os.environ['HOSTNAME']:
        patch("fx700.patch", when="%fj")

    def flag_handler(self, name, flags):
        spec = self.spec

        if name in ('cflags', 'cxxflags', 'fflags'):
            if spec.satisfies('+openmp'):
                if self.compiler.name == 'nvhpc':
                    flags.append('-mp')
                    flags = [f for f in flags if "fopenmp" not in f]
                else:
                    flags.append(self.compiler.openmp_flag)

                if self.compiler.name == 'fj':
                    flags.append('-Nfjomplib')

        return flags, None, None

    def cmake_args(self):
        spec = self.spec

        args = [
            self.define_from_variant("USE_EIGENEXA", "eigenexa"),
            self.define("USE_MPI", True),
            self.define_from_variant("USE_SCALAPACK", "scalapack"),
            self.define_from_variant("USE_LIBXC", "libxc"),
            self.define("CMAKE_VERBOSE_MAKEFILE", True),
        ]

        if spec.satisfies("build_type=Release"):
            args.append(self.define("CMAKE_BUILD_TYPE", "None"))
        else:
            args.append(self.define_from_variant("CMAKE_BUILD_TYPE", "build_type"))

        if self.compiler.name == 'fj':
            if spec.satisfies('+openmp'):
                ssl2_flag = "-SSL2BLAMP"
            else:
                ssl2_flag = "-SSL2"

            args += [
                self.define("CMAKE_Fortran_COMPILER", "mpifrt"),
                self.define("CMAKE_C_COMPILER", "mpifcc"),
                self.define("CMAKE_Fortran_FLAGS", "-Kfast -Kocl -Nlst=t -Koptmsg=2 -Ncheck_std=03s"),
                self.define("CMAKE_C_FLAGS", "-Kfast -Kocl -Nlst=t -Koptmsg=2 -Xg -std=gnu99"),
                self.define("CMAKE_C_STANDARD_COMPUTED_DEFAULT", "Fujitsu"),
                self.define("CMAKE_Fortran_MODDIR_FLAG", "-M "),
                self.define("OPENMP_FLAGS", "-Kopenmp -Nfjomplib"),
                self.define("LAPACK_VENDOR_FLAGS", ssl2_flag),
                self.define("Fortran_PP_FLAGS", "-Cpp"),
            ]

            if spec.satisfies('+scalapack'):
                args.append(self.define("ScaLAPACK_VENDOR_FLAGS", f"-SCALAPACK {ssl2_flag}"))

        elif self.compiler.name == 'nvhpc':
            args += [
                self.define("CMAKE_Fortran_COMPILER", "mpif90"),
                self.define("CMAKE_C_COMPILER", "mpicc"),
                self.define("OPENMP_FLAGS", "-Mnoopenmp"),
                self.define("USE_OPENACC", True),
                self.define("USE_MPI_DEFAULT", True),
                self.define("CMAKE_SYSTEM_PROCESSOR", "openacc"),
            ]

            if spec.satisfies('+cuda'):
                args += [
                    self.define(
                        "CMAKE_Fortran_FLAGS", 
                        "-O3 -Wall -fstrict-aliasing -acc=strict -gpu=cc90,cc100,cc120,managed,ptxinfo -cudalib=cublas -cuda -Minfo=accel -DUSE_OPENACC -DUSE_CUDA",
                    ),
                    self.define(
                        "CMAKE_C_FLAGS", 
                        "-O3 -Wall -alias=ansi -acc=strict -gpu=cc90,cc100,cc120,managed,ptxinfo -cudalib=cublas -cuda -Minfo=accel -DUSE_OPENACC -DUSE_CUDA",
                    ),
                    self.define(
                        "CMAKE_CUDA_FLAGS",
                        "",
                    ), 
                    self.define("USE_CUDA", True),
                ]

            else:
                args += [
                    self.define(
                        "CMAKE_Fortran_FLAGS", 
                        "-O3 -Wall -fstrict-aliasing -acc=strict -gpu=cc90,cc100,cc120,managed,ptxinfo -cudalib=cublas -cuda -Minfo=accel -DUSE_OPENACC",
                    ),
                    self.define(
                        "CMAKE_C_FLAGS", 
                        "-O3 -Wall -alias=ansi -acc=strict -gpu=cc90,cc100,cc120,managed,ptxinfo -cudalib=cublas -cuda -Minfo=accel -DUSE_OPENACC",
                    ),
                ]

        elif self.compiler.name == 'gcc':
            args += [
                self.define("CMAKE_Fortran_COMPILER", "mpif90"),
                self.define("CMAKE_C_COMPILER", "mpicc"),
                self.define("CMAKE_Fortran_FLAGS", "-O3 -ffree-line-length-none -fallow-argument-mismatch"),
                self.define("CMAKE_C_FLAGS", "-O3"),
            ]       
            
        return args

