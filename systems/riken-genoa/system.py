# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from benchpark.directives import maintainers, variant
from benchpark.openmpsystem import OpenMPCPUOnlySystem
from benchpark.paths import hardware_descriptions
from benchpark.system import System, compiler_def, compiler_section_for


class RikenGenoa(System):

    maintainers("jdomke", "SBA0486")

    id_to_resources = {
        "genoa": {
            "sys_cores_per_node": 96,
            "sys_mem_per_node_GB": 768,
            "system_site": "rccs",
            "queue": "genoa",
            "hardware_key": str(hardware_descriptions)
            + "/AMD-zen4-EPYC-Ethernet/hardware_description.yaml",
        },
    }

    variant(
        "compiler",
        default="gcc",
        values=("gcc",),
        description="Which compiler to use",
    )

    def __init__(self, spec):
        super().__init__(spec)
        self.programming_models = [OpenMPCPUOnlySystem()]
        self.scheduler = "slurm"

        attrs = self.id_to_resources.get("genoa")
        for k, v in attrs.items():
            setattr(self, k, v)

    def compute_packages_section(self):
        return {
            "packages": {
                "all": {
                    "providers": {
                        "mpi": ["fujitsu-mpi", "openmpi", "mpich"],
                        "blas": ["fujitsu-ssl2", "openblas"],
                        "lapack": ["fujitsu-ssl2", "openblas"],
                        "scalapack": ["fujitsu-ssl2", "netlib-scalapack"],
                        "fftw-api": ["fujitsu-fftw", "fftw", "rist-fftw"],
                    },
                    "permissions": {"write": "group"},
                },
                # The genoa nodes run Ubuntu 24.04 since the 2026-10 maintenance
                # (Rocky 9 before). Everything below is the distribution's own,
                # as found on the compute nodes: Open MPI 4.1.6 (built
                # --with-slurm and against PMIx), gcc 13.3.0, and the tools.
                "mpi": {
                    "externals": [
                        {
                            "spec": "openmpi@4.1.6",
                            "prefix": "/usr",
                            "extra_attributes": {
                                "ldflags": "-L/usr/lib/x86_64-linux-gnu/openmpi/lib -lmpi"
                            },
                        },
                    ],
                },
                "pkgconf": {
                    "externals": [
                        {
                            "spec": "pkgconf@1.8.1",
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
                "cmake": {
                    "externals": [
                        {
                            "spec": "cmake@3.28.3",
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
                "m4": {
                    "externals": [
                        {
                            "spec": "m4@1.4.19",
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
                "openssl": {
                    "externals": [
                        {
                            "spec": "openssl@3.0.13",
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
                "tar": {
                    "externals": [
                        {
                            "spec": "tar@1.35",
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
                "flex": {
                    "externals": [
                        {
                            "spec": "flex@2.6.4",
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
                "sed": {
                    "externals": [
                        {
                            "spec": "sed@4.9",
                            "prefix": "/usr",
                        }
                    ]
                },
                "autoconf": {
                    "externals": [
                        {
                            "spec": "autoconf@2.71",
                            "prefix": "/usr",
                        }
                    ]
                },
                "perl": {
                    "externals": [
                        {
                            "spec": "perl@5.38.2~cpanm+opcode+open+shared+threads",
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
                "libtool": {
                    "externals": [
                        {
                            "spec": "libtool@2.4.7",
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
            }
        }

    def compute_compilers_section(self):
        return compiler_section_for(
            "gcc",
            [
                compiler_def(
                    "gcc@13.3.0 languages:=c,c++,fortran",
                    "/usr/",
                    {"c": "gcc", "cxx": "g++", "fortran": "gfortran"},
                )
            ],
        )

    def system_specific_variables(self):
        return {
            "queue": "genoa",
            "pre_exec_cmds": "export SLURM_MPI_TYPE=pmix",
        }

    def compute_software_section(self):
        return {
            "software": {
                "packages": {
                    "default-compiler": {"pkg_spec": "gcc"},
                    "default-mpi": {"pkg_spec": "openmpi"},
                    "compiler-gcc": {"pkg_spec": "gcc"},
                    "blas": {"pkg_spec": "openblas"},
                    "lapack": {"pkg_spec": "openblas"},
                }
            }
        }
