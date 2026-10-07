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


class RikenRikyu(System):

    maintainers("jdomke", "SBA0486")

    id_to_resources = {
        "RIKYU": {
            "sys_cores_per_node": 144,
            "sys_gpus_per_node": 4,
            "sys_mem_per_node_GB": 960,
            "system_site": "rccs",
            "hardware_key": str(hardware_descriptions)
            + "/NVIDIA-neoverse-RIKYU-Infiniband/hardware_description.yaml",
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
        values=("16.2", "15.3", "14.4", "13.3"),
        description="GCC version",
    )
    variant(
        "cuda",
        default="13.2",
        values=("12.6", "12.9", "13.0", "13.1", "13.2", "13.3", "13.4"),
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
        values=("26.9", "26.5", "26.3", "25.11", "25.7", "24.9"),
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
        cuda_cuda_version = {
            "13.4": "13.4.2",
            "13.3": "13.3.1",
            "13.2": "13.2.2",
            "13.1": "13.2.2",
            "13.0": "13.2.2",
            "12.9": "12.9.2",
            "12.6": "12.6.3",
        }
        nvhpc_cuda_version = {
            "26.9": "13.3",
            "26.5": "13.2",
            "26.3": "13.1",
            "25.11": "13.0",
            "25.7": "12.9",
            "24.9": "12.6",
        }
        if self.spec.satisfies("compiler=nvhpc"):
            if str(self.nvhpc_version) == "25.7" or str(self.nvhpc_version) == "24.9":
                if str(self.nvhpc_flag) == "False" and str(pnt) == "system":
                    print("\n NVHPC@26.9 or 26.5 or 26.3 or 25.11 available.")
                    print(" Changing to nvhpc@26.3 and continuing the process.\n")
                    self.nvhpc_version = "26.3"
            self.cuda_version = nvhpc_cuda_version.get(
                str(self.nvhpc_version), self.cuda_version
            )
        else:
            if str(self.cuda_version) == "13.0" or str(self.cuda_version) == "13.1":
                if str(pnt) == "system":
                    print("\n Change the CUDA version to 13.2.2\n")
            if str(self.cuda_version) == "12.6":
                if str(self.cuda_flag) == "False" and str(pnt) == "system":
                    print("\n CUDA@13.4 or 13.3 or 13.2 or 12.9 available.")
                    print(" Changing to cuda@12.9 and continuing the process.\n")
                    self.cuda_version = "12.9"
            self.cuda_version = cuda_cuda_version.get(
                str(self.cuda_version), self.cuda_version
            )
        self.scheduler = "slurm"

        attrs = self.id_to_resources.get("RIKYU")
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
                "libaec": {
                    "externals": [
                        {
                            "spec": "libaec@1.1.4",
                            "prefix": "/data1/rkp00015/share/spack/opt/spack/neoverse_v2/libaec-1.1.4",
                        }
                    ]
                },
                "libevent": {
                    "externals": [
                        {
                            "spec": "libevent@2.1.12",
                            "prefix": "/data1/rkp00015/share/spack/opt/spack/neoverse_v2/libevent-2.1.12",
                        }
                    ]
                },
                "libiconv": {
                    "externals": [
                        {
                            "spec": "libiconv@1.18",
                            "prefix": "/data1/rkp00015/share/spack/opt/spack/neoverse_v2/libiconv-1.18",
                        }
                    ]
                },
                "libtool": {
                    "externals": [
                        {
                            "spec": "libtool@2.4.7",
                            "prefix": "/data1/rkp00015/share/spack/opt/spack/neoverse_v2/libtool-2.4.7",
                        }
                    ]
                },
                "lz4": {
                    "externals": [
                        {
                            "spec": "lz4@1.9.4",
                            "prefix": "/data1/rkp00015/share/spack/opt/spack/neoverse_v2/lz4-1.10.0",
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
                "apptainer": {
                    "externals": [
                        {
                            "spec": "apptainer@1.4.5",
                            "prefix": "/shared/software/apptainer",
                        }
                    ]
                },
                "singularity": {
                    "externals": [
                        {
                            "spec": "singularity@1.4.5",
                            "prefix": "/shared/software/apptainer",
                        }
                    ]
                },
                "slurm": {
                    "externals": [
                        {
                            "spec": "slurm@25.11.5",
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
                "zlib-ng": {
                    "externals": [
                        {
                            "spec": "zlib-ng@1.3",
                            "prefix": "/data1/rkp00015/share/spack/opt/spack/neoverse_v2/zlib-ng-2.3.2",
                        }
                    ]
                },
                "zstd": {
                    "externals": [
                        {
                            "spec": "zstd@1.5.5",
                            "prefix": "/data1/rkp00015/share/spack/opt/spack/neoverse_v2/zstd-1.5.7",
                        }
                    ]
                },
            }
        }
        if self.spec.satisfies("compiler=gcc") or self.spec.satisfies("compiler=cuda"):
            ompi_version = "4.1.8"
        else:
            cuda_version = self.cuda_version
            nvhpc_version = self.nvhpc_version
            if str(nvhpc_version) == "26.9" or str(nvhpc_version) == "26.5":
                ompi_version = "5.0.10"
            if str(nvhpc_version) == "26.3" or str(nvhpc_version) == "25.11":
                ompi_version = "4.1.9"
            if str(self.nvhpc_version) == "25.7" or str(self.nvhpc_version) == "24.9":
                ompi_version = "4.1.7"

        if self.spec.satisfies("compiler=nvhpc"):
            if str(nvhpc_version) == "25.7" or str(nvhpc_version) == "24.9":
                selections["packages"] |= {
                    "openmpi": {
                        "externals": [
                            {
                                "spec": f"openmpi@{ompi_version}",
                                "prefix": f"/data1/rkp00015/share/spack/opt/spack/neoverse_v2/nvhpc-{nvhpc_version}/Linux_aarch64/{self.nvhpc_version}/comm_libs/{self.cuda_version}/hpcx/latest/ompi",
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
                                "prefix": f"/shared/software/hpc_sdk/Linux_aarch64/{nvhpc_version}/comm_libs/{cuda_version}/hpcx/latest/ompi",
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
                            "prefix": "/shared/mpi/openmpi/4.1.8_ubuntu",
                        },
                    ],
                },
            }
        if self.spec.satisfies("compiler=nvhpc"):
            selections["packages"] |= self.cuda_config()["packages"]

        return selections

    def cuda_config(self):
        nvhpc_version = self.nvhpc_version
        cuda_version = self.cuda_version
        if str(nvhpc_version) == "25.7" or str(nvhpc_version) == "24.9":
            return {
                "packages": {
                    "cuda": {
                        "externals": [
                            {
                                "spec": f"cuda@{cuda_version}",
                                "prefix": f"/data1/rkp00015/share/spack/opt/spack/neoverse_v2/nvhpc-{nvhpc_version}/Linux_aarch64/{nvhpc_version}/cuda/{cuda_version}",
                            }
                        ],
                        "buildable": False,
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
                                "prefix": f"/shared/software/hpc_sdk/Linux_aarch64/{nvhpc_version}/cuda/{cuda_version}",
                            }
                        ],
                        "buildable": False,
                    },
                }
            }

    def compute_compilers_section(self):
        if str(self.gcc_version) == "13.3":
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
            gcc_cfg = compiler_section_for(
                "gcc",
                [
                    compiler_def(
                        f"gcc@{self.gcc_version} languages:=c,c++,fortran",
                        f"/data1/rkp00015/share/spack/opt/spack/neoverse_v2/gcc-{self.gcc_version}.0",
                        {"c": "gcc", "cxx": "g++", "fortran": "gfortran"},
                    )
                ],
            )
        if self.spec.satisfies("compiler=cuda"):
            if str(self.cuda_version) != "12.6.3":
                cuda_cfg = compiler_section_for(
                    "cuda",
                    [
                        compiler_def(
                            f"cuda@{self.cuda_version}",
                            f"/shared/software/cuda/{self.cuda_version}",
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
                            f"/data1/rkp00015/share/spack/opt/spack/neoverse_v2/cuda-{self.cuda_version}",
                            {"c": "nvcc", "cxx": "nvcc"},
                        )
                    ],
                )
            return merge_dicts(cuda_cfg, gcc_cfg)
        if self.spec.satisfies("compiler=nvhpc"):
            nvhpc_version = self.nvhpc_version
            if str(nvhpc_version) == "25.7" or str(nvhpc_version) == "24.9":
                return compiler_section_for(
                    "nvhpc",
                    [
                        compiler_def(
                            f"nvhpc@{self.nvhpc_version}",
                            f"/data1/rkp00015/share/spack/opt/spack/neoverse_v2/nvhpc-{nvhpc_version}",
                            {
                                lang: f"/data1/rkp00015/share/spack/opt/spack/neoverse_v2/nvhpc-{nvhpc_version}/Linux_aarch64/{self.nvhpc_version}/compilers/bin/{exe}"
                                for lang, exe in (
                                    ("c", "nvc"),
                                    ("cxx", "nvc++"),
                                    ("fortran", "nvfortran"),
                                )
                            },
                            extra_rpaths=[
                                f"/data1/rkp00015/share/spack/opt/spack/neoverse_v2/nvhpc-{nvhpc_version}/Linux_aarch64/{nvhpc_version}/math_libs/lib64",
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
                            # The SDK root, not .../compilers. spack's nvhpc
                            # package appends Linux_<arch>/<version>/compilers
                            # when locating libblas and liblapack, so a deeper
                            # prefix resolves to a path that does not exist and
                            # dependents receive an empty library list. The
                            # compiler drivers are given as absolute paths,
                            # since compiler_def joins bare names to the prefix.
                            "/shared/software/hpc_sdk",
                            {
                                lang: f"/shared/software/hpc_sdk/Linux_aarch64/{self.nvhpc_version}/compilers/bin/{exe}"
                                for lang, exe in (
                                    ("c", "nvc"),
                                    ("cxx", "nvc++"),
                                    ("fortran", "nvfortran"),
                                )
                            },
                            extra_rpaths=[
                                f"/shared/software/hpc_sdk/Linux_aarch64/{nvhpc_version}/math_libs/lib64",
                            ],
                        )
                    ],
                )
        return gcc_cfg

    def system_specific_variables(self):
        pre_exec = ["export SLURM_MPI_TYPE=pmix"]

        nvhpc_hpcx_versions = ("26.9", "26.5", "26.3", "25.11")
        if self.spec.satisfies("compiler=nvhpc") and str(self.nvhpc_version) in nvhpc_hpcx_versions:
            hpcx = (
                f"/shared/software/hpc_sdk/Linux_aarch64/{self.nvhpc_version}"
                f"/comm_libs/{self.cuda_version}/hpcx/latest"
            )
            pre_exec += [
                f"source {hpcx}/hpcx-init.sh",
                "hpcx_load",
                "export PMIX_MCA_psec=native",
            ]

        nvhpc_hpcx_versions = ("25.7", "24.9")
        if self.spec.satisfies("compiler=nvhpc") and str(self.nvhpc_version) in nvhpc_hpcx_versions:
            hpcx = (
                f"/data1/rkp00015/share/spack/opt/spack/neoverse_v2/nvhpc-{self.nvhpc_version}"
                f"/Linux_aarch64/{self.nvhpc_version}"
                f"/comm_libs/{self.cuda_version}/hpcx/latest"
            )
            pre_exec += [
                f"source {hpcx}/hpcx-init.sh",
                "hpcx_load",
                "export PMIX_MCA_psec=native",
            ]

        return {
            "cuda_arch": "100",
            "pre_exec_cmds": "; ".join(pre_exec),
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
