# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

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

    version('2.3.0', tag='v.2.3.0')
    version('2.2.2', tag='v.2.2.2')
    version('2.2.1', tag='v.2.2.1')
    version('2.2.0', tag='v.2.2.0')
    version('2.1.0', tag='v.2.1.0')
    version('2.0.2', tag='v.2.0.2')
    version('2.0.1', tag='v.2.0.1')
    version('2.0.0', tag='v.2.0.0')

    version('develop', branch='develop-2.0.0')

    depends_on("c", type="build")
    depends_on("fortran", type="build")

    variant("build_type", default="Release", values=("Release", "Debug"))
    variant("openmp", default=False, description="Enable OpenMP")
    variant("openacc", default=False, description="Enable OpenACC")
    variant("libxc", default=False, description="Enable libxc")
    variant("scalapack", default=False, description="Enable scalapack")
    variant("eigenexa", default=False, description="Enable eigenexa")
    variant("cuda", default=False, description="Enable cuda")
    variant("rocm", default=False, description="Enable rocm")
    variant("fx700", default=False, description="Use the FX700 MPI rank mapping")

    depends_on("cmake@3.14:", type="build")
    depends_on("cmake@3.18:", type="build", when="+cuda")
    depends_on("mpi", type=("build", "link"))
    depends_on("scalapack", type="link", when="+scalapack")
    depends_on("eigenexa", type="link", when="+eigenexa")
    depends_on("libxc", type="link", when="+libxc")
    depends_on("lapack", type="link", when="%gcc")

    conflicts("+eigenexa", when="~scalapack")
    conflicts("+openacc", when="+openmp")
    conflicts("+cuda", when="~openacc")
    conflicts("+cuda", when="%gcc")
    conflicts("+cuda", when="%fj")
    conflicts("+cuda", when="%clang")
    conflicts("+openacc", when="%gcc")
    conflicts("+openacc", when="%fj")
    conflicts("+openacc", when="%clang")
    conflicts("+rocm")
    conflicts("+fx700", when="%gcc")
    conflicts("+fx700", when="%nvhpc")

    patch("fx700_no_tofu_mapping.patch", when="+fx700 %fj")

    # NVHPC 26.9 serializes this OpenACC kernels loop in 2.2.2 and 2.3.0.
    patch("nvhpc_26_9_pz_parallel.patch", when="@2.2.2 +openacc %nvhpc@26.9")
    patch("nvhpc_26_9_pz_parallel.patch", when="@2.3.0 +openacc %nvhpc@26.9")

    # The tau operator is unavailable under OpenACC, but its eight-dimensional
    # arrays still exceed NVHPC's rank limit when the unused body is compiled.
    patch("nvhpc_2_3_0_tau_operator.patch", when="@2.3.0 +openacc %nvhpc")

    # Zero inactive reduction lanes and release CUDA current-work buffers.
    patch("cuda_stencil_current.patch", when="@2.0.2:2.3.0 +cuda")
    patch("cuda_stencil_current.patch", when="@develop +cuda")

    # Version-specific FX700 fixes are separate from the shared MPI mapping patch.
    patch("fx700_v2.2.2.patch", when="@2.2.2 +fx700 %fj")
    patch("fx700_v2.2.2.patch", when="@2.3.0 +fx700 %fj")
    patch("fx700_develop.patch", when="@develop +fx700 %fj")


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
        ]

        if spec.satisfies("build_type=Release"):
            pass
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
                self.define("CMAKE_Fortran_FLAGS", "-Kfast -Kocl"),
                self.define("CMAKE_C_FLAGS", "-Kfast -Kocl -Xg -std=gnu99"),
                self.define("CMAKE_C_STANDARD_COMPUTED_DEFAULT", "Fujitsu"),
                self.define("CMAKE_Fortran_MODDIR_FLAG", "-M "),
                self.define("OPENMP_FLAGS", "-Kopenmp -Nfjomplib"),
                self.define("LAPACK_VENDOR_FLAGS", ssl2_flag),
                self.define("Fortran_PP_FLAGS", "-Cpp"),
            ]

            if spec.satisfies('+scalapack'):
                args.append(self.define("ScaLAPACK_VENDOR_FLAGS", f"-SCALAPACK {ssl2_flag}"))

        elif self.compiler.name == 'nvhpc':
            # Use consistent loop-bound evaluation for release and develop builds.
            # NVHPC >=26.5 can otherwise read stale device bounds in release sources.
            tripcount_flags = (
                ' -gpu=tripcount:host'
                if spec.satisfies('+openacc %nvhpc@26.5:')
                else ''
            )
            args += [
                self.define("CMAKE_Fortran_COMPILER", self.spec["mpi"].mpifc),
                self.define("CMAKE_C_COMPILER", self.spec["mpi"].mpicc),
                self.define("USE_MPI_DEFAULT", True),
                self.define_from_variant("USE_OPENACC", "openacc"),
            ]

            if not spec.satisfies('+openmp'):
                args.append(self.define("OPENMP_FLAGS", "-Mnoopenmp"))

            # Keep NVHPC-only library flags out of the global executable flags:
            # CMake tests CUDA with g++, which cannot accept -cudalib.
            cuda_math_flags = '-cudalib=cublas'
            if spec.satisfies('@develop +openacc') or spec.satisfies('@2.3.0 +openacc'):
                cuda_math_flags += ',cusolver'
            args.append(self.define('CMAKE_EXE_LINKER_FLAGS', '-Wl,-z,muldefs'))
            args.append('-DCMAKE_SHARED_LINKER_FLAGS=-Wl,-z,muldefs')

            if spec.satisfies('+cuda'):
                args += [
                    self.define(
                        "CMAKE_Fortran_FLAGS", 
                        f"-O3 -Wall -fstrict-aliasing -acc=strict -gpu=cc90,cc100,cc120,managed {cuda_math_flags} -cuda -DUSE_OPENACC -DUSE_CUDA" + tripcount_flags,
                    ),
                    self.define(
                        "CMAKE_C_FLAGS", 
                        f"-O3 -Wall -alias=ansi -acc=strict -gpu=cc90,cc100,cc120,managed {cuda_math_flags} -cuda -DUSE_OPENACC -DUSE_CUDA" + tripcount_flags,
                    ),
                    self.define(
                        "CMAKE_CUDA_FLAGS",
                        "",
                    ), 
                    # Match the native OpenACC targets; avoid a PTX-only fallback
                    # on drivers older than the compiler's bundled CUDA toolkit.
                    self.define("CMAKE_CUDA_ARCHITECTURES", "90;100;120"),
                    self.define("USE_CUDA", True),
                ]

            elif spec.satisfies('+openacc'):
                args += [
                    self.define(
                        "CMAKE_Fortran_FLAGS", 
                        f"-O3 -Wall -fstrict-aliasing -acc=strict -gpu=cc90,cc100,cc120,managed {cuda_math_flags} -cuda -DUSE_OPENACC" + tripcount_flags,
                    ),
                    self.define(
                        "CMAKE_C_FLAGS", 
                        f"-O3 -Wall -alias=ansi -acc=strict -gpu=cc90,cc100,cc120,managed {cuda_math_flags} -cuda -DUSE_OPENACC" + tripcount_flags,
                    ),
                ]

        elif self.compiler.name == 'gcc':
            if not spec.satisfies('+openmp'):
                # SALMON calls OpenMP timer routines even without parallel regions.
                args.append(self.define("CMAKE_Fortran_STANDARD_LIBRARIES", "-lgomp"))
            args += [
                self.define("OPENMP_FLAGS", "-fopenmp" if spec.satisfies("+openmp") else "-fno-openmp"),
                self.define("CMAKE_Fortran_COMPILER", self.spec["mpi"].mpifc),
                self.define("CMAKE_C_COMPILER", self.spec["mpi"].mpicc),
                self.define("CMAKE_Fortran_FLAGS", "-O3 -ffree-line-length-none -fallow-argument-mismatch"),
                self.define("CMAKE_C_FLAGS", "-O3"),
            ]       
            
        return args
