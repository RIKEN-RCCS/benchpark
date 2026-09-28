# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import os

from spack_repo.builtin.build_systems.generic import Package
from spack.package import *


class Ffb(Package):
    homepage = "http://www.ciss.iis.u-tokyo.ac.jp/project/rss/software/07_info.html"
    url = ""

    version("67.01-cpu", sha256="beba53067ce9f4097cba30cc79a3198718f823e4887e2c290785245eb44de2ed", url="file:///vol0003/rccs-sdt/data/a01008/apps/ffb/ffb-frt_cpu.fugaku.tar.gz")
    version("67.01-cpu-genoa", sha256="623b99b9b2644ca68d98bfe092ed3fcc57bae373e20f8bc2697d33a8730c80d6", url="file:///lvs0/rccs-sdt/kazuto.ando/apps/ffb/ffb-frt_cpu.genoa.ftz.tar.gz")
    version("67.01-gpu-gh200", sha256="9629ce4a97c295cbfdc4df0bcfaf6efe12919ff7aa438e812b26f438c60d22ba", url="file:///lvs0/rccs-sdt/kazuto.ando/apps/ffb/ffb-acc_gpu.gh.tar.gz")

    # The archive compiles C, C++ and Fortran and links against MPI.
    #
    # The language dependencies are not optional documentation: since spack's
    # compilers became nodes in the DAG, a compiler constraint attaches to a
    # package through them, so a package that declares none cannot carry one.
    # `%nvhpc` then reaches the concretizer with nothing to attach it to and
    # the solve ends in
    #
    #     internal_error("Imposing constraint outside of imposed_nodes")
    #     internal_error("nodes in root condition set must be associated
    #                     with root")
    depends_on("c", type="build")
    depends_on("cxx", type="build")
    depends_on("fortran", type="build")
    depends_on("gmake", type="build")
    depends_on("mpi", type=("build", "link", "run"))

    def setup_build_environment(self, env):
        # make/OPTION reads ${MPI_HOME} for its include and library paths.
        env.set("MPI_HOME", self.spec["mpi"].prefix)

    def install(self, spec, prefix):
        has_cuda = "gpu" in str(spec)

        if has_cuda:
            # The archive names its toolchain by bare command name in three
            # places, which is how the machine's module environment provides
            # it. A spack build environment has none of those names on PATH,
            # so each sub-build stops at once:
            #
            #     make: mpif90: No such file or directory
            #     make[1]: nvc++: No such file or directory
            #     mpicc: symbol lookup error: undefined symbol: PMIx_Info_create
            #
            # and install fails with no binary to install. Substitute the
            # wrappers and compilers spack resolved instead.
            mpicc = spec["mpi"].mpicc
            mpifc = spec["mpi"].mpifc
            filter_file(r"^CCOM[ \t]*=.*", f"CCOM = {mpicc}", "make/OPTION")
            filter_file(r"^FCOM[ \t]*=.*", f"FCOM = {mpifc}", "make/OPTION")
            filter_file(r"^LINK[ \t]*=.*", f"LINK = {mpifc}", "make/OPTION")
            filter_file(
                r"^CC[ \t]*=[ \t]*mpicc[ \t]*$",
                f"CC = {mpicc}",
                join_path("lib", "src", "ParMetis-3.1", "Makefile.in"),
            )
            refiner = join_path(
                "lib", "src", "REVOCAP_Refiner-1.1.02", "MakefileConfig.in"
            )
            filter_file(r"^CC[ \t]*=[ \t]*nvc[ \t]*$", f"CC = {spack_cc}", refiner)
            filter_file(r"^CXX[ \t]*=[ \t]*nvc\+\+[ \t]*$", f"CXX = {spack_cxx}", refiner)
            filter_file(r"^F90[ \t]*=[ \t]*nvfortran[ \t]*$", f"F90 = {spack_fc}", refiner)
            filter_file(
                r"^LDSHARED[ \t]*=[ \t]*nvc\+\+ ",
                f"LDSHARED = {spack_cxx} ",
                refiner,
            )

        chmod = which("chmod")
        chmod("+x", "make.FP3.sh")

        bash = which("bash")
        bash("./make.FP3.sh")

        if has_cuda:
            exe = "bin.acc_gpu/les3x.mpi"
        else:
            exe = "bin/les3x.mpi"

        mkdir(prefix.bin)
        install(exe, prefix.bin)

