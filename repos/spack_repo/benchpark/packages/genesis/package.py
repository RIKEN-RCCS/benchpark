# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from spack.package import *
from spack_repo.builtin.build_systems.autotools import AutotoolsPackage
#<<<<<<< HEAD:repo/genesis/package.py
from spack_repo.builtin.build_systems.cuda import CudaPackage
import os
#=======
#>>>>>>> upstream/develop:repos/spack_repo/benchpark/packages/genesis/package.py


class Genesis(AutotoolsPackage, CudaPackage):
    """GENESIS package contains two MD programs (atdyn and spdyn), trajectory
    analysis programs, and other useful tools. GENESIS (GENeralized-Ensemble
    SImulation System) has been developed mainly by Sugita group in RIKEN-CCS.
    """
    
    tags = ['genesis','benchmark']
    
    homepage = "https://mdgenesis.org/"
    git = "https://github.com/genesis-release-r-ccs/genesis"

    version("main", branch="main", submodules=False)
    version(
        "2.1.6", submodules=False, tag="v2.1.6", commit="025e9eba262ac9f1b5447573b5ad73af87cfc4b0"
    )
    version(
        "2.1.5", submodules=False, tag="v2.1.5", commit="5c5ac814a4ab081a6852362444ef88d50c1e9d0f"
    )
    version(
        "2.1.4", submodules=False, tag="v2.1.4", commit="48fa5654ae1ecdf606fb6cd0bdcc2952f5caaa65"
    )
    version(
        "2.1.3", submodules=False, tag="v2.1.3", commit="835ef1538f9350cfa7e9489f340837d0908afbd2"
    )
    version(
        "2.1.1", submodules=False, tag="v2.1.1", commit="38a54fe1c749f4d87bff591e65c61b23a7396f9d"
    )
    version(
        "2.0.3", submodules=False, tag="v2.0.3", commit="6989e0b24470e374ea343b2b7b685aca87909571"
    )

    variant("mpi", default=True, description="Build with MPI.")
    variant("openmp", default=True, description="Build with OpenMP enabled.")
    variant("lapack", default=True, description="Build with LAPACK enabled.")
    variant("gpu", default=False, description="Build with GPGPU enabled.")
    variant("precision", description="Build with selected precision.", default="double", values=("double", "mixed", "single"), multi=False)
    variant("simd", description="Build with SIMD width.", default="auto", values=("auto", "MIC-AVX512", "CORE-AVX512", "CORE-AVX2"), multi=False)
    variant("debug", description="Set Debug level", default="0", values=("0", "1", "2", "3", "4"), multi=False)

    # Has Fortran but I didn't see c/c++ code
    depends_on("c", type="build")
    depends_on("cxx", type="build")
    depends_on("fortran", type="build")

    depends_on("mpi", when="+mpi")
    depends_on("lapack", when="+lapack")
    depends_on("cuda", when="+gpu")

    def autoreconf(self, spec, prefix):
        bash = which("bash")
        bash("./bootstrap")

    @run_before("configure")
    def fix_programming_error(self):
        spec = self.spec
        if self.version < Version("2.1.3"):
            filter_file(r"atomcls1\(1:3\)", "atomcls1(1:6)", join_path(self.stage.source_path, "src/analysis/sp_analysis/hbond_analysis/hbond_analyze.fpp"))
            filter_file(r"atomcls2\(1:3\)", "atomcls2(1:6)", join_path(self.stage.source_path, "src/analysis/sp_analysis/hbond_analysis/hbond_analyze.fpp"))

    def configure_args(self):
        spec = self.spec
        args = []

        precision = spec.variants["precision"].value
        args.append(f"--enable-{precision}")

        simd = spec.variants["simd"].value
        args.append(f"--with-simd={simd}")

        debug_level = int(spec.variants['debug'].value) 
        if debug_level > 0:
            args.append(f"--enable-debug={debug_level}")

        args.append("--enable-mpi" if "+mpi" in spec else "--disable-mpi")
        args.append("--enable-openmp" if "+openmp" in spec else "--disable-openmp")
        args.append("--with-lapack" if "+lapack" in spec else "--without-lapack")
        args.append("--enable-gpu" if "+gpu" in spec else "--disable-gpu")

        if "+mpi" in spec:
            env["CC"] = spec["mpi"].mpicc
            env["CXX"] = spec["mpi"].mpicxx
            env["FC"] = spec["mpi"].mpifc
            env["F77"] = spec["mpi"].mpif77

        if "+openmp" in spec and spec.satisfies("%clang"):
            env["OPT_OPENMP"] = "-fopenmp"

        if spec.satisfies("%clang"):
            opt_flags = "-Ofast -ffast-math"
            env["CFLAGS"] = f"{opt_flags}"
            env["CXXFLAGS"] = f"{opt_flags}"
            env["FCFLAGS"] = f"{opt_flags} -Mbackslash"
            env["F77FLAGS"] = f"{opt_flags} -Mbackslash"
            # cpp workaround; other systems and OS likely need different pre-processor fix
            if spec.target == "a64fx":
                env["FPP"] = "/opt/FJSVxtclanga/tcsds-1.2.38/bin/../lib/fpp"
                env["PPFLAGS"] = "-traditional-cpp -traditional"
        elif spec.satisfies("%fj"):
            opt_flags = "-Kfast"
            env["CFLAGS"] = f"{opt_flags}"
            env["CXXFLAGS"] = f"{opt_flags}"
            env["FCFLAGS"] = f"{opt_flags}"
            env["F77FLAGS"] = f"{opt_flags}"
            if spec.target == "a64fx":
                # Using same flags as the version installed outside benchpark
                env["CFLAGS"] = "-Kfast -Kocl -Kswp"
                env["FCFLAGS"] = "-Kocl -Kfast -Kopenmp -Nlst=t -Koptmsg=2"
                env["LDFLAGS"] = "-SSL2BLAMP -Kparallel -Kopenmp -Nlibomp"
                # if Lapack_libs is not specified, build fails when linking
                env["LAPACK_LIBS"] = spec["lapack"].libs.ld_flags
        elif spec.satisfies("%gcc"):
            opt_flags = "-O3 -ffast-math"
            env["CFLAGS"] = f"{opt_flags}"
            env["CXXFLAGS"] = f"{opt_flags}"
            env["FCFLAGS"] = f"{opt_flags} -ffree-line-length-none"
            env["F77FLAGS"] = f"{opt_flags} -ffree-line-length-none"

        return args

    def setup_build_environment(self, env: EnvironmentModifications) -> None:
        spec = self.spec

        if self.spec.satisfies("+lapack"):
            env.set("LAPACK_LIBS", self.spec["lapack"].libs.ld_flags)

        if self.spec.satisfies("+gpu") and "cuda" in spec:
            cuda_arch_variant = self.spec.variants.get("cuda_arch", None)

            if cuda_arch_variant is None:
                cuda_arch_list = ["90"]
            else:
                cuda_arch_list = list(cuda_arch_variant.value)

                cuda_arch_list = [a for a in cuda_arch_list if a != "none"]
                if not cuda_arch_list:
                    cuda_arch_list = ["90"]

            cuda_gencode = " ".join(self.cuda_flags(cuda_arch_list))
            env.set("NVCCFLAGS", cuda_gencode)

            cuda_prefix = spec["cuda"].prefix

            inc_dirs = [
                join_path(cuda_prefix, "include"),
                join_path(cuda_prefix, "targets", "sbsa-linux", "include"),
                join_path(cuda_prefix, "targets", "sbsa-linux", "include", "nvtx3"),
            ]
            lib_dirs = [
                join_path(cuda_prefix, "lib64"),
                join_path(cuda_prefix, "targets", "sbsa-linux", "lib"),
            ]

            for d in inc_dirs:
                if os.path.isdir(d):
                    env.prepend_path("CPATH",d)
                    env.prepend_path("CPLUS_INCLUDE_PATH",d)
                    env.prepend_path("C_INCLUDE_PATH",d)

                    env.append_flags("CFLAGS",    f"-I{d}")
                    env.append_flags("CXXFLAGS",  f"-I{d}")
                    env.append_flags("CPPFLAGS",  f"-I{d}")
                    env.append_flags("NVCCFLAGS", f"-I{d}")

            for d in lib_dirs:
                if os.path.isdir(d):
                    env.append_flags("LDFLAGS", f"-L{d}")
                    env.prepend_path("LD_LIBRARY_PATH", d)

            env.set("CUDA_HOME", str(cuda_prefix))
            env.set("CUDA_PATH", str(cuda_prefix))
