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
    version("67.01-gpu", sha256="9629ce4a97c295cbfdc4df0bcfaf6efe12919ff7aa438e812b26f438c60d22ba", url="file:///lvs0/rccs-sdt/kazuto.ando/apps/ffb/ffb-acc_gpu.gh.tar.gz")

    def install(self, spec, prefix):
        has_cuda = "gpu" in str(spec)

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

