# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import sys
from packaging.version import Version

from benchpark.cudasystem import CudaSystem
from benchpark.directives import maintainers, variant
from benchpark.openmpsystem import OpenMPCPUOnlySystem
from benchpark.paths import hardware_descriptions
from benchpark.system import (
    System,
    compiler_def,
    compiler_section_for,
    merge_dicts,
)


class RikenDgx(System):

    maintainers("jdomke", "SBA0486")

    id_to_resources = {
        "dgx": {
            "sys_cores_per_node": 20,
            "sys_gpus_per_node": 1,
            "sys_mem_per_node_GB": 128,
            "system_site": "rccs",
            "queue": "ng-dgx-s",
            "hardware_key": str(hardware_descriptions)
            + "/NVIDIA-cortex-GB10-Ethernet/hardware_description.yaml",
        },
    }

    variant(
        "compiler",
        default="gcc",
        values=("gcc", "nvhpc", "cuda"),
        description="Which compiler to use",
    )
    variant(
        "gcc",
        default="13.3",
        values=("13.3", "14.3", "15.2"),
        description="GCC version",
    )
    variant(
        "cuda",
        default="13.2",
        values=("13.2", "13.0", "12.9", "12.6", "12.4"),
        description="CUDA version",
    )
    variant(
        "cuda12",
        default=False,
        values=(True, False),
        description="CUDA 12 series, ON/OFF",
    )
    variant(
        "nvhpc",
        default="26.9",
        values=("26.9", "26.5", "26.3", "25.9", "25.7", "24.3"),
        description="NVHPC version",
    )
    variant(
        "nvhpc25",
        default=False,
        values=(True, False),
        description="NVHPC 24 series, ON/OFF",
    )
    variant(
        "bank",
        default="none",
        description="Submit a job to a specific named bank",
    )

    def __init__(self, spec):
        super().__init__(spec)
        self.programming_models = [CudaSystem(), OpenMPCPUOnlySystem()]
        self.gcc_version = Version(self.spec.variants["gcc"][0])
        self.cuda_version = Version(self.spec.variants["cuda"][0])
        self.cuda_flag = self.spec.variants["cuda12"][0]
        self.nvhpc_version = Version(self.spec.variants["nvhpc"][0])
        self.nvhpc_flag = self.spec.variants["nvhpc25"][0]
        pnt = sys.argv[1]
        nvhpc_cuda_version = {
            "26.9": "13.3",
            "26.5": "13.2",
            "26.3": "13.1",
            "25.9": "13.0",
            "25.7": "12.9",
            "24.3": "12.3",
        }
        if self.spec.satisfies("compiler=nvhpc"):
            if str(self.nvhpc_version).split(".")[0] != "26":
                if str(self.nvhpc_flag) == "False" and str(pnt) == "system":
                    print("\n NVHPC@26.9 or 26.5 or 26.3 available.")
                    print(" Changing to nvhpc@26.3 and continuing the process.\n")
                if str(self.nvhpc_flag) == "False":
                    self.nvhpc_version = "26.3"
            self.cuda_version = nvhpc_cuda_version.get(
                str(self.nvhpc_version), self.cuda_version
            )
        else:
            if str(self.cuda_version).split(".")[0] == "12":
                if str(self.cuda_flag) == "False" and str(pnt) == "system":
                    print("\n CUDA 12 series has been deleted by the administrator.")
                    print(" Changing to cuda@13.0 and continuing the process.\n")
                if str(self.cuda_flag) == "False":
                    self.cuda_version = "13.0"
        self.scheduler = "slurm"

        attrs = self.id_to_resources.get("dgx")
        for k, v in attrs.items():
            setattr(self, k, v)

    def compute_packages_section(self):
        selections = {
            "packages": {
                "all": {
                    "providers": {
                        "mpi": ["openmpi"],
                        "blas": ["openblas"],
                        "lapack": ["openblas"],
                        "scalapack": ["netlib-scalapack"],
                        "fftw-api": ["fftw"],
                    },
                    "permissions": {"write": "group"},
                },
                "autoconf": {
                    "externals": [
                        {
                            "spec": "autoconf@2.71",
                            "prefix": "/usr",
                        }
                    ]
                },
                "automake": {
                    "externals": [
                        {
                            "spec": "automake@1.16.5",
                            "prefix": "/usr",
                        }
                    ]
                },
                "binutils": {
                    "externals": [
                        {
                            "spec": "binutils@2.42",
                            "prefix": "/usr",
                        }
                    ]
                },
                "bzip2": {
                    "externals": [
                        {
                            "spec": "bzip2@1.0.8",
                            "prefix": "/usr",
                        }
                    ]
                },
                "bison": {
                    "externals": [
                        {
                            "spec": "bison@3.8.2",
                            "prefix": "/usr",
                        }
                    ]
                },
                "cmake": {
                    "externals": [
                        {
                            "spec": "cmake@3.28.3",
                            "prefix": "/usr",
                        }
                    ]
                },
                "coreutils": {
                    "externals": [
                        {
                            "spec": "coreutils@9.4",
                            "prefix": "/usr",
                        }
                    ]
                },
                "curl": {
                    "externals": [
                        {
                            "spec": "curl@8.5.0",
                            "prefix": "/usr",
                        }
                    ]
                },
                "diffutils": {
                    "externals": [
                        {
                            "spec": "diffutils@3.10",
                            "prefix": "/usr",
                        }
                    ]
                },
                "findutils": {
                    "externals": [
                        {
                            "spec": "findutils@4.9.0",
                            "prefix": "/usr",
                        }
                    ]
                },
                "flex": {
                    "externals": [
                        {
                            "spec": "flex@2.6.4",
                            "prefix": "/usr",
                        }
                    ]
                },
                "gawk": {
                    "externals": [
                        {
                            "spec": "gawk@5.2.1",
                            "prefix": "/usr",
                        }
                    ]
                },
                "gettext": {
                    "externals": [
                        {
                            "spec": "gettext@0.21",
                            "prefix": "/usr",
                        }
                    ]
                },
                "git": {
                    "externals": [
                        {
                            "spec": "git@2.43.0",
                            "prefix": "/usr",
                        }
                    ]
                },
                "gmake": {
                    "externals": [
                        {
                            "spec": "gmake@4.3",
                            "prefix": "/usr",
                        }
                    ]
                },
                "groff": {
                    "externals": [
                        {
                            "spec": "groff@1.23.0",
                            "prefix": "/usr",
                        }
                    ]
                },
                "libevent": {
                    "externals": [
                        {
                            "spec": "libevent@2.1.12",
                            "prefix": "/lvs0/rccs-nghpcadu/share/spack/opt/spack/cortex_x925/libevent-2.1.12",
                        }
                    ]
                },
                "libiconv": {
                    "externals": [
                        {
                            "spec": "libiconv@1.18",
                            "prefix": "/lvs0/rccs-nghpcadu/share/spack/opt/spack/cortex_x925/libiconv-1.18",
                        }
                    ]
                },
                "libtool": {
                    "externals": [
                        {
                            "spec": "libtool@2.4.7",
                            "prefix": "/lvs0/rccs-nghpcadu/share/spack/opt/spack/cortex_x925/libtool-2.4.7",
                        }
                    ]
                },
                "m4": {
                    "externals": [
                        {
                            "spec": "m4@1.4.19",
                            "prefix": "/usr",
                        }
                    ]
                },
                "openssh": {
                    "externals": [
                        {
                            "spec": "openssh@9.6p1",
                            "prefix": "/usr",
                        }
                    ]
                },
                "openssl": {
                    "externals": [
                        {
                            "spec": "openssl@3.0.13",
                            "prefix": "/usr",
                        }
                    ]
                },
                "perl": {
                    "externals": [
                        {
                            "spec": "perl@5.38.2",
                            "prefix": "/usr",
                        }
                    ]
                },
                "pkgconf": {
                    "externals": [
                        {
                            "spec": "pkgconf@1.8.1",
                            "prefix": "/usr",
                        }
                    ]
                },
                "python": {
                    "externals": [
                        {
                            "spec": "python@3.12.3",
                            "prefix": "/usr",
                        }
                    ]
                },
                "sed": {
                    "externals": [
                        {
                            "spec": "sed@4.9",
                            "prefix": "/usr",
                        }
                    ]
                },
                "singularity": {
                    "externals": [
                        {
                            "spec": "singularity@4.1.1",
                            "prefix": "/usr",
                        }
                    ]
                },
                "slurm": {
                    "externals": [
                        {
                            "spec": "slurm@24.05.8",
                            "prefix": "/usr",
                        }
                    ]
                },
                "tar": {
                    "externals": [
                        {
                            "spec": "tar@1.35",
                            "prefix": "/usr",
                        }
                    ]
                },
                "xz": {
                    "externals": [
                        {
                            "spec": "xz@5.4.5",
                            "prefix": "/usr",
                        }
                    ]
                },
                "zstd": {
                    "externals": [
                        {
                            "spec": "zstd@1.5.5",
                            "prefix": "/usr",
                        }
                    ]
                },
            }
        }
        if self.spec.satisfies("compiler=gcc") or self.spec.satisfies("compiler=cuda"):
            ompi_version = "4.1.8"
        else:
            ompi_dir = "ompi"
            if str(self.nvhpc_version) == "26.5" or str(self.nvhpc_version) == "26.9":
                ompi_version = "4.1.9"
                ompi_dir = "ompi4"
            if str(self.nvhpc_version) == "26.3" or str(self.nvhpc_version) == "25.9":
                ompi_version = "4.1.9"
            if str(self.nvhpc_version) == "25.7" or str(self.nvhpc_version) == "24.3":
                ompi_version = "4.1.7"

        if self.spec.satisfies("compiler=nvhpc"):
            if str(self.nvhpc_version).split(".")[0] == "26":
                selections["packages"] |= {
                    "openmpi": {
                        "externals": [
                            {
                                "spec": f"openmpi@{ompi_version}",
                                "prefix": f"/opt/nvidia/hpc_sdk/Linux_aarch64/{self.nvhpc_version}/comm_libs/{self.cuda_version}/hpcx/latest/{ompi_dir}",
                            },
                        ],
                    },
                }
            else:
                selections["packages"] |= {
                    "openmpi": {
                        "externals": [
                            {
                                "spec": f"openmpi@{ompi_version}",
                                "prefix": f"/lvs0/rccs-nghpcadu/share/spack/opt/spack/cortex_x925/nvhpc-{self.nvhpc_version}/Linux_aarch64/{self.nvhpc_version}/comm_libs/{self.cuda_version}/hpcx/latest/ompi",
                            },
                        ],
                    },
                }
        else:
            selections["packages"] |= {
                "openmpi": {
                    "externals": [
                        {
                            "spec": f"openmpi@{ompi_version}",
                            "prefix": "/lvs0/rccs-nghpcadu/share/spack/opt/spack/cortex_x925/openmpi-4.1.8",
                        },
                    ],
                },
            }

        if not self.spec.satisfies("compiler=cuda"):
            selections["packages"] |= self.cuda_config()["packages"]

        return selections

    def cuda_config(self):
        cuda_version = self.cuda_version
        if self.spec.satisfies("compiler=nvhpc"):
            if str(self.nvhpc_version).split(".")[0] == "26":
                return {
                    "packages": {
                        "cuda": {
                            "externals": [
                                {
                                    "spec": f"cuda@{cuda_version}",
                                    "prefix": f"/opt/nvidia/hpc_sdk/Linux_aarch64/{self.nvhpc_version}/cuda/{cuda_version}",
                                }
                            ],
                        },
                    }
                }
            else:
                return {
                    "packages": {
                        "cuda": {
                            "externals": [
                                {
                                    "spec": f"cuda@{cuda_version}",
                                    "prefix": f"/lvs0/rccs-nghpcadu/share/spack/opt/spack/cortex_x925/nvhpc-{self.nvhpc_version}/Linux_aarch64/{self.nvhpc_version}/cuda/{cuda_version}",
                                }
                            ],
                        },
                    }
                }
        else:
            return {
                "packages": {
                    "cuda": {
                        "externals": [
                            {
                                "spec": f"cuda@{self.cuda_version}",
                                "prefix": f"/usr/local/cuda-{self.cuda_version}",
                            },
                        ],
                    },
                }
            }

    def compute_compilers_section(self):
        gcc_version = self.gcc_version
        if str(self.gcc_version).split(".")[0] == "13":
            gcc_cfg = compiler_section_for(
                "gcc",
                [
                    compiler_def(
                        "gcc@13.3.0 languages:=c,c++,fortran",
                        "/usr/",
                        {"c": "gcc", "cxx": "g++", "fortran": "gfortran"},
                    )
                ],
            )
        else:
            if str(self.gcc_version) == "14.3":
                gcc_version = "14.3.0"
            if str(self.gcc_version) == "15.2":
                gcc_version = "15.2.0"
            gcc_cfg = compiler_section_for(
                "gcc",
                [
                    compiler_def(
                        f"gcc@{gcc_version} languages:=c,c++,fortran",
                        f"/lvs0/rccs-nghpcadu/share/spack/opt/spack/cortex_x925/gcc-{gcc_version}",
                        {"c": "gcc", "cxx": "g++", "fortran": "gfortran"},
                    )
                ],
            )
        if self.spec.satisfies("compiler=cuda"):
            if str(self.cuda_version).split(".")[0] == "12":
                if str(self.cuda_version) == "12.9":
                    cuda_version = "12.9.1"
                if str(self.cuda_version) == "12.6":
                    cuda_version = "12.6.3"
                if str(self.cuda_version) == "12.4":
                    cuda_version = "12.4.1"
                cuda_cfg = compiler_section_for(
                    "cuda",
                    [
                        compiler_def(
                            f"cuda@{cuda_version}",
                            f"/lvs0/rccs-nghpcadu/share/spack/opt/spack/cortex_x925/cuda-{cuda_version}",
                            {"c": "nvcc", "cxx": "nvcc"},
                        )
                    ],
                )
            else:
                cuda_cfg = compiler_section_for(
                    "cuda",
                    [
                        compiler_def(
                            f"cuda@{self.cuda_version}",
                            f"/usr/local/cuda-{self.cuda_version}",
                            {"c": "nvcc", "cxx": "nvcc"},
                        )
                    ],
                )
            return merge_dicts(cuda_cfg, gcc_cfg)
        if self.spec.satisfies("compiler=nvhpc"):
            if str(self.nvhpc_version).split(".")[0] == "26":
                return compiler_section_for(
                    "nvhpc",
                    [
                        compiler_def(
                            f"nvhpc@{self.nvhpc_version}",
                            # The SDK root, not .../compilers. spack's nvhpc
                            # package appends Linux_<arch>/<version>/compilers
                            # when locating libblas and liblapack, so a deeper
                            # prefix resolves to a path that does not exist and
                            # dependents receive an empty library list. The
                            # compiler drivers are given as absolute paths,
                            # since compiler_def joins bare names to the prefix.
                            "/opt/nvidia/hpc_sdk",
                            {
                                lang: f"/opt/nvidia/hpc_sdk/Linux_aarch64/{self.nvhpc_version}/compilers/bin/{exe}"
                                for lang, exe in (
                                    ("c", "nvc"),
                                    ("cxx", "nvc++"),
                                    ("fortran", "nvfortran"),
                                )
                            },
                            extra_rpaths=[
                                f"/opt/nvidia/hpc_sdk/Linux_aarch64/{self.nvhpc_version}/math_libs/lib64",
                            ],
                        )
                    ],
                )
            else:
                return compiler_section_for(
                    "nvhpc",
                    [
                        compiler_def(
                            f"nvhpc@{self.nvhpc_version}",
                            f"/lvs0/rccs-nghpcadu/share/spack/opt/spack/cortex_x925/nvhpc-{self.nvhpc_version}",
                            {
                                lang: f"/lvs0/rccs-nghpcadu/share/spack/opt/spack/cortex_x925/nvhpc-{self.nvhpc_version}/Linux_aarch64/{self.nvhpc_version}/compilers/bin/{exe}"
                                for lang, exe in (
                                    ("c", "nvc"),
                                    ("cxx", "nvc++"),
                                    ("fortran", "nvfortran"),
                                )
                            },
                            extra_rpaths=[
                                f"/lvs0/rccs-nghpcadu/share/spack/opt/spack/cortex_x925/nvhpc-{self.nvhpc_version}/Linux_aarch64/{self.nvhpc_version}/math_libs/lib64",
                            ],
                        )
                    ],
                )
        return gcc_cfg

    def system_specific_variables(self):
        ompi_dir = "ompi"
        if str(self.nvhpc_version) == "26.5" or str(self.nvhpc_version) == "26.9":
            ompi_dir = "ompi4"
        cmds=""
        pre_exec = "export SLURM_MPI_TYPE=pmix"
        if self.spec.satisfies("compiler=nvhpc"):
            if str(self.nvhpc_version) != "26.5" and str(self.nvhpc_version) != "26.9":
                pre_exec += ";export OMPI_MCA_coll=^hcoll"
            if str(self.nvhpc_version).split(".")[0] == "26":
                libdirs = [f"/opt/nvidia/hpc_sdk/Linux_aarch64/{self.nvhpc_version}"
                           f"/comm_libs/{self.cuda_version}/hpcx/latest/{d}/lib" 
                           for d in (f"{ompi_dir}", "ucx", "ucc", "hcoll", "sharp")
                ]
                pre_exec += (
                    f"; export OPAL_PREFIX=/opt/nvidia/hpc_sdk/Linux_aarch64/{self.nvhpc_version}"
                    f"/comm_libs/{self.cuda_version}/hpcx/latest/{ompi_dir}"
                    f"; export LD_LIBRARY_PATH={':'.join(libdirs)}:$LD_LIBRARY_PATH"
                )
            else:
                libdirs = [f"/lvs0/rccs-nghpcadu/share/spack/opt/spack/cortex_x925"
                           f"/nvhpc-{self.nvhpc_version}/Linux_aarch64/{self.nvhpc_version}"
                           f"/comm_libs/{self.cuda_version}/hpcx/latest/{d}/lib"
                           for d in (f"{ompi_dir}", "ucx", "ucc", "hcoll", "sharp")
                ]
                pre_exec += (
                    f"; export OPAL_PREFIX=/lvs0/rccs-nghpcadu/share/spack/opt/spack/cortex_x925"
                    f"/nvhpc-{self.nvhpc_version}/Linux_aarch64/{self.nvhpc_version}"
                    f"/comm_libs/{self.cuda_version}/hpcx/latest/{ompi_dir}"
                    f"; export LD_LIBRARY_PATH={':'.join(libdirs)}:$LD_LIBRARY_PATH"
                )
        return {
            "cuda_arch": "121",
            "queue": "ng-dgx-s",
            "pre_exec_cmds": pre_exec,
        }

    def compute_software_section(self):
        default_comp = self.spec.variants["compiler"][0]
        return {
            "software": {
                "packages": {
                    "default-compiler": {"pkg_spec": f"{default_comp}"},
                    "default-mpi": {"pkg_spec": "openmpi"},
                    "compiler-gcc": {"pkg_spec": "gcc"},
                    "compiler-nvhpc": {"pkg_spec": "nvhpc"},
                    "cublas-cuda": {"pkg_spec": "cublas"},
                    "blas": {"pkg_spec": "openblas"},
                    "lapack": {"pkg_spec": "openblas"},
                }
            }
        }
