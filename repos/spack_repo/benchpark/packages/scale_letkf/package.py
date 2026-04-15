# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import os
import glob
from spack_repo.builtin.build_systems.makefile import MakefilePackage
from spack.package import *

class ScaleLetkf(MakefilePackage):
    """SCALE (Scalable Computing for Advanced Library and Environment) is
    a basic library for weather and climate model of the earth and planets
    aimed to be widely used in various models.
    LETKF (Local Ensemble Transform Kalman Filter) is a kind of data assimilation.
    This program is comblined of the above two for benchmark test."""

    homepage = "https://github.com/SCALE-LETKF-RIKEN/scale-letkf-FugakuNEXT"
    git = "https://github.com/SCALE-LETKF-RIKEN/scale-letkf-FugakuNEXT.git"

    license("BSD-2-Clause")

    version("master", branch="master", submodules=False)

    depends_on("c", type="build")
    depends_on("fortran", type="build")
    depends_on("cxx", type="build", when="%nvhpc")
    depends_on("gmake", type="build")

    depends_on("mpi@2:", type=("build", "link", "run"))
    depends_on("cuda", type=("build", "link", "run"), when="%nvhpc")
    depends_on("netcdf-c")
    depends_on("netcdf-fortran")
    depends_on("parallel-netcdf")
    depends_on("lapack")

    patch("fj-own_compiler.patch", when="%fj", working_dir="scale")

    def setup_build_environment(self, env: EnvironmentModifications) -> None:
        env.set("PREFIX", self.prefix)
        target_family = str(self.spec.target.family)

        # set SCALE_SYS
        scale_sys_str = ""

        if target_family == "x86_64" and self.spec.satisfies("%gcc"):
            scale_sys_str = "Linux64-gnu-ompi"
        elif target_family == "aarch64" and self.spec.satisfies("%gcc"):
            scale_sys_str = "LinuxARM-gnu-ompi"
        elif self.spec.satisfies("%nvhpc"):
            scale_sys_str = "Linux64-nvidia"
        elif self.spec.satisfies("%fj"): # FUGAKU/FX700
            env.set("SCALE_USE_AGGRESSIVEOPT", "F")
            scale_sys_str = "FUGAKU"

        if scale_sys_str == "":
            raise InstallError("unsupported arch and compiler combination.")
        env.set("SCALE_SYS", scale_sys_str)

        nc_config = Executable(os.path.join(self.spec['netcdf-c'].prefix.bin, "nc-config"))
        nf_config = Executable(os.path.join(self.spec['netcdf-fortran'].prefix.bin, "nf-config"))

        # set SCALE_NETCDF_INCLUDE
        nc_str = nc_config("--cflags", output=str).strip()
        nf_str = nf_config("--fflags", output=str).strip()
        env.set("SCALE_NETCDF_INCLUDE", "{} {}".format(nc_str, nf_str))

        # set SCALE_NETCDF_LIBS
        nc_libs = nc_config("--libs", output=str).strip()
        nf_libs = nf_config("--flibs", output=str).strip()
        env.set("SCALE_NETCDF_LIBS", "{} {}".format(nc_libs, nf_libs))

        # set OPENMP/OPENACC
        if self.spec.satisfies("%nvhpc"):
            env.set("SCALE_ENABLE_OPENMP", "F")
            env.set("SCALE_ENABLE_OPENACC", "T")
        else:
            env.set("SCALE_ENABLE_OPENMP", "T")
            env.set("SCALE_ENABLE_OPENACC", "F")

        # set SCALE_MATHLIB_LIBS
        if 'lapack' in self.spec:
            try:
                lapack_libs = self.spec['lapack'].libs.ld_flags
            except:
                lapack_libs = ""

            if not lapack_libs or lapack_libs.strip() == "":
                if self.spec['lapack'].name == 'nvhpc':
                    lapack_libs = "-lblas -llapack"
                else:
                    try:
                        prefix = self.spec['lapack'].prefix
                        if prefix:
                            lapack_libs = "-L{0}/lib -L{0}/lib64 -lopenblas".format(prefix)
                    except:
                        pass

            if self.spec.satisfies("%nvhpc") and "cuda" in self.spec:
                cuda_lib = self.spec['cuda'].prefix.lib64
                lapack_libs += f" -L{cuda_lib}"
                if self.spec['lapack'].name == 'nvhpc':
                    try:
                        prefix_path = str(self.spec['lapack'].prefix)
                        nvhpc_root = os.path.abspath(os.path.join(prefix_path, ".."))
                        math_libs = os.path.join(nvhpc_root, "math_libs/lib64")
                        lapack_libs += f" -L{math_libs}"
                    except:
                        pass

            if lapack_libs:
                env.set("SCALE_MATHLIB_LIBS", lapack_libs)
                env.set("SCALE_ENABLE_MATHLIB", "T")

    def build(self, spec, prefix):
        with working_dir("scale/scale-rm/src"):
            make()
        with working_dir("scale/scale-letkf/scale"):
            make()

    def install(self, spec, prefix):
        mkdirp(prefix.bin)
        install("scale/scale-letkf/scale/ensmodel/scale-rm_ens", prefix.bin)
        install("scale/scale-letkf/scale/ensmodel/scale-rm_init_ens", prefix.bin)
        install("scale/scale-letkf/scale/ensmodel/scale-rm_pp_ens", prefix.bin)
        install("scale/scale-letkf/scale/letkf/letkf", prefix.bin)

        mkdirp(prefix.share)
        bench_dirs = glob.glob(os.path.join("test", "benchmark*"))
        for d in bench_dirs:
            install_tree(d, os.path.join(prefix.share, os.path.basename(d)))
