# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import os

from spack_repo.builtin.build_systems.generic import Package
from spack.package import *


class Ffb(Package):
    homepage = "http://www.ciss.iis.u-tokyo.ac.jp/project/rss/software/07_info.html"
    url = "file:///lvs0/rccs-sdt/kazuto.ando/apps/ffb/ffb-acc_gpu.gh.tar.gz"

    version("main", sha256="9629ce4a97c295cbfdc4df0bcfaf6efe12919ff7aa438e812b26f438c60d22ba")

    depends_on("nvhpc", type="build")

    def install(self, spec, prefix):

        chmod = which("chmod")
        chmod("+x", "make.FP3.sh")

        bash = which("bash")
        bash("./clean.sh")
        bash("./make.FP3.sh")

        exe = "bin.acc_gpu/les3x.mpi"

        mkdir(prefix.bin)
        install(exe, prefix.bin)
