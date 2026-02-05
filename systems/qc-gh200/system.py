# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from benchpark.system import System, JobQueue, compiler_def, compiler_section_for, merge_dicts
from benchpark.directives import variant, maintainers
from benchpark.openmpsystem import OpenMPCPUOnlySystem
from benchpark.cudasystem import CudaSystem
from packaging.version import Version
from benchpark.paths import hardware_descriptions


class QcGh200(System):
    id_to_resources = {
        "gh200": {
            "sys_cores_per_node": 72,
            "sys_gpus_per_node": 1,
            "sys_mem_per_node_GB": 512,
            "system_site": "rccs",
            "queue": "qc-gh200",
            "hardware_key": str(hardware_descriptions)
            + "/qc-gh200/hardware_description.yaml",
        },
        "fx700": {
            "sys_cores_per_node": 48,
            "sys_gpus_per_node": 1,
        },
        "genoa": {
            "sys_cores_per_node": 96,
            "sys_gpus_per_node": 1,
        }
    }

    variant(
        "cluster",
        default="gh200",
        values=("gh200", "fx700", "genoa"),
        description="Which cluster to run on",
    )
    variant(
        "compiler",
        default="gcc",
        values=("gcc", "cuda_12.5", "cuda", "nvhpc_24.3", "nvhpc_24.9", "nvhpc"),
        description="Which compiler to use",
    )
    variant(
        "cuda",
        default="12.9",
        values=("12.5", "12.9"),
        description="CUDA version",
    )
    variant(
        "gtl",
        default=False,
        values=(True, False),
        description="Use GTL-enabled MPI",
    )

    def __init__(self, spec):
        super().__init__(spec)
        self.programming_models = [CudaSystem(), OpenMPCPUOnlySystem()]
        self.cuda_version = Version(self.spec.variants["cuda"][0])
        self.gtl_flag = self.spec.variants["gtl"][0]

        full_versions = {
            "gcc": "11.5.0",
            "cuda": "12.9",
            "cuda125": "12.5",
            "nvhpc243": "24.3",
            "nvhpc249": "24.9",
            "nvhpc257": "25.7",
        }
        for key, value in full_versions.items():
            if key == self.spec.variants["compiler"][0]:
                self.compiler_version = Version(value)

        self.scheduler = "slurm"
        attrs = self.id_to_resources.get(self.spec.variants["cluster"][0])
        for k, v in attrs.items():
            setattr(self, k, v)

    def system_specific_variables(self):
        return {
            "cuda_arch": "90",
            "queue": "qc-gh200",
            "pre_exec_cmds": "export SLURM_MPI_TYPE=pmix",
        }

    def compute_software_section(self):
        """This is somewhat vestigial, and maybe deleted later. The experiments
        will fail if these variables are not defined though, so for now
        they are still generated (but with more-generic values).
        """
        return {
            "software": {
                "packages": {
                    "default-compiler": {"pkg_spec": "gcc"},
                    "default-mpi": {"pkg_spec": "openmpi"},
                    "compiler-gcc": {"pkg_spec": "gcc"},
                    "compiler-nvhpc": {"pkg_spec": "nvhpc"},
                    "cublas-cuda": {"pkg_spec": f"cublas"},
                    "blas": {"pkg_spec": "openblas"},
                    "lapack": {"pkg_spec": "openblas"},
                }
            }
        }

    def compute_packages_section(self):
        if self.spec.satisfies("compiler=nvhpc"):
           selections = {
               "packages": {
                   "nvhpc": {
                       "externals": [
                           {
                               "spec": f"nvhpc@25.7",
                               "modules": [
                                   "system/qc-gh200",
                                   "nvhpc/25.7",
                               ],
                           },
                       ],
                   },
               }
           }

        if self.spec.satisfies("compiler=nvhpc_24.3"):
           selections = {
               "packages": {
                   "nvhpc": {
                       "externals": [
                           {
                               "spec": f"nvhpc@24.3",
                               "modules": [
                                   "system/qc-gh200",
                                   "nvhpc/24.3",
                               ],
                           },
                       ],
                   },
               }
           }

        if self.spec.satisfies("compiler=nvhpc_24.9"):
           selections = {
               "packages": {
                   "nvhpc": {
                       "externals": [
                           {
                               "spec": f"nvhpc@24.9",
                               "modules": [
                                   "system/qc-gh200",
                                   "nvhpc/24.9",
                               ],
                           },
                       ],
                   },
               }
           }

        if (self.spec.satisfies("compiler=gcc") or
            self.spec.satisfies("compiler=cuda_12.5") or
            self.spec.satisfies("compiler=cuda")):
           selections = {
               "packages": {
                   "mpi": {
                       "externals": [
                           {
                               "spec": f"openmpi@4.1.7",
                               "prefix": f"/usr/mpi/gcc/openmpi-4.1.7rc1",
                               "extra_attributes": {
                                   "ldflags": "-L/usr/mpi/gcc/openmpi-4.1.7rc1/lib64 -lmpi"
                               },
                           },
                       ],
                   },
               }
           }

        make_selections = {
            "packages": {
                "cmake": {
                    "externals": [
                        {
                            "spec": f"cmake@3.26.5",
                            "prefix": f"/usr",
                        },
                    ],
                },
                "gmake": {
                    "externals": [
                        {
                            "spec": f"gmake@4.3",
                            "prefix": f"/usr",
                        },
                    ],
                },
            }
        }
        all_selections = merge_dicts(selections, make_selections)

        return all_selections

    def compute_compilers_section(self):
        gcc_cfg = compiler_section_for(
            "gcc",
            [
                compiler_def(
                    "gcc@11.5.0 languages:=c,c++,fortran",
                    "/usr/",
                    {"c": "gcc", "cxx": "g++", "fortran": "gfortran"},
                )
            ],
        )
        if self.spec.satisfies("compiler=cuda"):
            cuda_cfg = compiler_section_for(
                "cuda",
                [
                    compiler_def(
                        "cuda@12.9",
                        "/usr/local/cuda-12.9",
                        {"c": "nvcc", "cxx": "nvcc"},
                    )
                ],
            )
            cfg = merge_dicts(cuda_cfg, gcc_cfg)
        else:
            if self.spec.satisfies("compiler=cuda_12.5"):
                cuda_cfg = compiler_section_for(
                    "cuda",
                    [
                        compiler_def(
                            "cuda@12.5",
                            "/usr/local/cuda-12.5",
                            {"c": "nvcc", "cxx": "nvcc"},
                        )
                    ],
                )
                cfg = merge_dicts(cuda_cfg, gcc_cfg)
            else:
                cfg = gcc_cfg

        return cfg

