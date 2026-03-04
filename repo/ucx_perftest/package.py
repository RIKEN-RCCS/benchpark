# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0
import os
import inspect

import llnl.util.filesystem as fs
from spack.package import *
from spack_repo.builtin.build_systems.cuda import CudaPackage

class UcxPerftest(AutotoolsPackage, CudaPackage):
    tags = []

    url = "https://github.com/openucx/ucx/releases/download/v1.19.0/ucx-1.19.0.tar.gz"
    git = "https://github.com/openucx/ucx"

    version("master", branch="master")
    version("1.19", tag="v1.19.0")

    variant("cuda", default=False, description="Build with CUDA")
    variant("cuda_arch", default="90", description="CUDA architecture")
    variant("verbs", default=False, description="Build OpenFabrics support")
    variant("rc", default=False, description="Compile with IB Reliable Connection support")
    variant("ud", default=False, description="Compile with IB Unreliable Datagram support")
    variant("dc", default=False, description="Compile with IB Dynamic Connection support")
    variant("ib_hw_tm", default=False, description="Compile with IB Tag Matching support")
    variant("rdmacm", default=False, description="Enable the use of RDMACM")
    variant("mlx5", default=False, description="Compile with mlx5 Direct Verbs support")

    depends_on("c", type="build")
    depends_on("cxx", type="build")
    depends_on("cuda", when="+cuda")
    depends_on("rdma-core", when="+verbs")
    depends_on("rdma-core", when="+rdmacm")

    depends_on("autoconf", type="build")
    depends_on("automake", type="build")
    depends_on("libtool", type="build")
    depends_on("m4", type="build")

    def configure_args(self):
        args = super().configure_args()

        if self.spec.satisfies("+cuda"):
            args = [a for a in args if not a.startswith('--with-cuda=')]
            cuda_prefix = self.spec['cuda'].prefix
            args.append(f"--with-cuda={cuda_prefix}")
        else:
            args.append(f"--without-cuda")

        for v in ["verbs", "rc", "ud", "dc", "ib-hw-tm", "rdmacm", "mlx5"]:
            v_spec = v.replace("-", "_")
            if f"+{v_spec}" in self.spec:
                args.append(f"--with-{v}")
            else:
                args.append(f"--without-{v}")

        return args
