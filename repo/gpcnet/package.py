# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0
import inspect

import llnl.util.filesystem as fs
from spack.package import *


class Gpcnet(MakefilePackage):
    tags = []

    url = "https://github.com/netbench/tags/1.2.tar.gz"
    git = "https://github.com/netbench/GPCNET"

    version("master", branch="master")
    version("1.2", tag="1.2")

    depends_on("c", type="build")
    depends_on("mpi")

    def edit(self, spec, prefix):
        filter_file(r"^CC\s*=.*", "CC = {0}".format(spec['mpi'].mpicc), "Makefile")

    def install(self, spec, prefix):
        mpicc = spec["mpi"].mpicc
        make("all", "CC={0}".format(mpicc))
        mkdirp(prefix.bin)
        install("network_test", prefix.bin)
        install("network_load_test", prefix.bin)
