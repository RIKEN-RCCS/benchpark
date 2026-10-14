# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0


from benchpark.directives import maintainers, variant
from benchpark.openmpsystem import OpenMPCPUOnlySystem
from benchpark.paths import hardware_descriptions
from benchpark.system import System, compiler_def, compiler_section_for


class RikenFugaku(System):

    maintainers("jdomke", "SBA0486")

    id_to_resources = {
        "fugaku": {
            "cpu_arch": "A64FX",
            "sys_cores_per_node": 48,
            "sys_mem_per_node_GB": 32,
            "system_site": "riken",
            "queue": "small",
            "hardware_key": str(hardware_descriptions)
            + "/Fujitsu-A64FX-TofuD/hardware_description.yaml",
        },
    }

    variant(
        "compiler",
        default="clang",
        values=("clang", "gcc", "fj"),
        description="Which compiler to use",
    )

    def __init__(self, spec):
        super().__init__(spec)
        self.programming_models = [OpenMPCPUOnlySystem()]

        self.scheduler = "pjm"
        attrs = self.id_to_resources.get("fugaku")
        for k, v in attrs.items():
            setattr(self, k, v)

    def compute_packages_section(self):
        # Doesn't look like we need to switch MPI based on compiler from old definition, verify this
        # SBA: It is actually needed for fujitsu-mpi and fujitsu-ssl2. Edited to load the required version only.
        default_comp = self.spec.variants["compiler"][0]
        if default_comp == "clang":
            comp_version = "clang@19.1.4"
            mpi_prefix = "/opt/FJSVxtclanga/tcsds-mpi-1.2.43"
            ssl2_prefix = "/vol0004/apps/oss/llvm-v19.1.4/compute_node"
        if default_comp == "fj":
            comp_version = "fj@4.12.2"
            mpi_prefix = "/opt/FJSVxtclanga/tcsds-mpi-1.2.43"
            ssl2_prefix = "/opt/FJSVxtclanga/tcsds-ssl2-1.2.43"
        if default_comp == "gcc":
            comp_version = "gcc@13.2.0"
            mpi_prefix = "/vol0004/apps/oss/mpigcc/fjmpi-gcc12"
            ssl2_prefix = "/opt/FJSVxtclanga/tcsds-ssl2-1.2.43"

        if self.spec.satisfies("compiler=fj"):
            selections = {
                "packages": {
                    "all": {
                        "compiler": ["llvm", "fj", "gcc"],
                        "providers": {
                            "mpi": ["fujitsu-mpi", "openmpi"],
                            "blas": ["fujitsu-ssl2", "openblas"],
                            "lapack": ["fujitsu-ssl2", "openblas"],
                            "scalapack": ["fujitsu-ssl2", "netlib-scalapack"],
                            "fftw-api": ["fujitsu-fftw", "fftw"],
                        },
                        "permissions": {"write": "group"},
                    },
                    "htslib": {"version": [1.12]},
                    "openssh": {"permissions": {"write": "user"}},
                    "fujitsu-mpi": {
                        "buildable": False,
                        "externals": [
                            {
                                "spec": "fujitsu-mpi@4.12.2 arch=linux-rhel8-a64fx %"
                                f"{comp_version}",
                                "prefix": f"{mpi_prefix}",
                            },
                        ],
                    },
                    "fujitsu-ssl2": {
                        "buildable": False,
                        "externals": [
                            {
                                "spec": "fujitsu-ssl2@4.12.2 arch=linux-rhel8-a64fx %"
                                f"{comp_version}",
                                "prefix": f"{ssl2_prefix}",
                            },
                        ],
                    },
                    "autoconf": {
                        "externals": [
                            {
                                "spec": "autoconf@2.69 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    #                    "automake": {
                    #                        "externals": [
                    #                            {
                    #                                "spec": "automake@1.16.1 arch=linux-rhel8-a64fx",
                    #                                "prefix": "/usr",
                    #                            }
                    #                        ]
                    #                    },
                    "binutils": {
                        "externals": [
                            {
                                "spec": "binutils@2.30 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "bzip2": {
                        "externals": [
                            {
                                "spec": "bzip2@1.0.6 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "curl": {
                        "externals": [
                            {
                                "spec": "curl@7.61.1 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "dbus": {
                        "externals": [
                            {
                                "spec": "dbus@1.12.8 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "elfutils": {
                        "externals": [
                            {
                                "spec": "elfutils@0.190 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            },
                        ]
                    },
                    "expat": {
                        "externals": [
                            {
                                "spec": "expat@2.5.0 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "findutils": {
                        "externals": [
                            {
                                "spec": "findutils@4.6.0 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "fontconfig": {
                        "externals": [
                            {
                                "spec": "fontconfig@2.13.1 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "freetype": {
                        "externals": [
                            {
                                "spec": "freetype@2.9.1 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "gmake": {
                        "externals": [
                            {
                                "spec": "gmake@4.2.1 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "gdbm": {
                        "externals": [
                            {
                                "spec": "gdbm@1.18 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "gettext": {
                        "externals": [
                            {
                                "spec": "gettext@0.19.8.1 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "gmp": {
                        "externals": [
                            {
                                "spec": "gmp@6.1.2 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "gnutls": {
                        "externals": [
                            {
                                "spec": "gnutls@3.6.16 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            },
                        ]
                    },
                    "hwloc": {
                        "externals": [
                            {
                                "spec": "hwloc@2.2.0 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "jansson": {
                        "externals": [
                            {
                                "spec": "jansson@2.14 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "libaio": {
                        "externals": [
                            {
                                "spec": "libaio@0.3.112 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "libcap": {
                        "externals": [
                            {
                                "spec": "libcap@2.48 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "libdrm": {
                        "externals": [
                            {
                                "spec": "libdrm@2.4.115 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            },
                        ]
                    },
                    "libedit": {
                        "externals": [
                            {
                                "spec": "libedit@3.1 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "libevent": {
                        "externals": [
                            {
                                "spec": "libevent@2.1.8 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "libffi": {
                        "externals": [
                            {
                                "spec": "libffi@3.1 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "libglvnd": {
                        "externals": [
                            {
                                "spec": "libglvnd@1.3.4 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "libpciaccess": {
                        "externals": [
                            {
                                "spec": "libpciaccess@0.14 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "libpng": {
                        "externals": [
                            {
                                "spec": "libpng@1.6.34 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "libtasn1": {
                        "externals": [
                            {
                                "spec": "libtasn1@4.13 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "libtirpc": {
                        "externals": [
                            {
                                "spec": "libtirpc@1.1.4 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "libtool": {
                        "externals": [
                            {
                                "spec": "libtool@2.4.6 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "libuuid": {
                        "externals": [
                            {
                                "spec": "libuuid@2.32.1 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "libxcb": {
                        "externals": [
                            {
                                "spec": "libxcb@1.13.1 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "libxkbcommon": {
                        "externals": [
                            {
                                "spec": "libxkbcommon@0.9.1 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "libxml2": {
                        "externals": [
                            {
                                "spec": "libxml2@2.9.7 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "lz4": {
                        "externals": [
                            {
                                "spec": "lz4@1.8.3 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "m4": {
                        "externals": [
                            {
                                "spec": "m4@1.4.18 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "mpi": {"buildable": False},
                    "nettle": {
                        "externals": [
                            {
                                "spec": "nettle@3.4.1 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "nspr": {
                        "externals": [
                            {
                                "spec": "nspr@4.36.0 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            },
                        ]
                    },
                    "numactl": {
                        "externals": [
                            {
                                "spec": "numactl@2.0.16 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "openssl": {
                        "buildable": False,
                        "externals": [
                            {
                                "spec": "openssl@1.1.1k arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            },
                        ],
                    },
                    "papi": {
                        "externals": [
                            {
                                "spec": "papi@5.6.0 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "pcre": {
                        "externals": [
                            {
                                "spec": "pcre@8.42 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "pcre2": {
                        "externals": [
                            {
                                "spec": "pcre2@10.32 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "perl": {
                        "externals": [
                            {
                                "spec": "perl@5.26.3 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "pkgconf": {
                        "externals": [
                            {
                                "spec": "pkgconf@1.4.2 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "popt": {
                        "externals": [
                            {
                                "spec": "popt@1.18 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    # The OS's own python 3.12 (python3.12 in /usr/bin on
                    # both login and compute nodes since the 2026-10
                    # maintenance). caliper needs a python to build, and
                    # without an external spack builds python@3.14 with fj,
                    # which fails: fj's clang accepts -mavx2 on A64FX, so
                    # CPython compiles its AVX2 Blake2b code and stops on
                    # Lib_IntVector_Intrinsics_vec256.
                    "python": {
                        "externals": [
                            {
                                "spec": "python@3.12.14 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "readline": {
                        "externals": [
                            {
                                "spec": "readline@7.0 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "sqlite": {
                        "externals": [
                            {
                                "spec": "sqlite@3.26.0 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "tcl": {
                        "externals": [
                            {
                                "spec": "tcl@8.6.8 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "valgrind": {
                        "externals": [
                            {
                                "spec": "valgrind@3.22.0 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            },
                        ]
                    },
                    "xz": {
                        "externals": [
                            {
                                "spec": "xz@5.2.4 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                    "zlib": {
                        "buildable": False,
                        "externals": [
                            {
                                "spec": "zlib@1.2.11 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ],
                    },
                }
            }
        else:
            selections = {
                "packages": {
                    "all": {
                        "compiler": ["gcc"],
                        "providers": {
                            "mpi": ["openmpi"],
                            "blas": ["openblas"],
                            "lapack": ["openblas"],
                            "scalapack": ["netlib-scalapack"],
                            "fftw-api": ["fftw"],
                        },
                        "permissions": {"write": "group"},
                    },
                    "singularity": {
                        "externals": [
                            {
                                "spec": "singularity@4.4.0 arch=linux-rhel8-a64fx",
                                "prefix": "/usr",
                            }
                        ]
                    },
                }
            }

        if not self.spec.satisfies("compiler=gcc"):
            selections["packages"] |= {
                "blas": {"require": ["fujitsu-ssl2"]},
                "lapack": {"require": ["fujitsu-ssl2"]},
            }

        return selections

    def compute_compilers_section(self):
        compiler = self.spec.variants["compiler"][0]

        if compiler == "clang":
            # maybe_flags = {
            #    "cflags": {"-msve-vector-bits=scalable"},
            #    "cxxflags": {"-msve-vector-bits=scalable"},
            #    "fflags": {"-msve-vector-bits=scalable"},
            #    "ldflags": {"-fuse-ld=lld"},
            # }
            cfg = compiler_section_for(
                "llvm",
                [
                    compiler_def(
                        "llvm@19.1.4",
                        "/vol0004/apps/oss/llvm-v19.1.4/compute_node/",
                        {"c": "clang", "cxx": "clang++", "fortran": "flang"},
                        env={
                            "append_path": {
                                "LD_LIBRARY_PATH": "/opt/FJSVxtclanga/tcsds-1.2.43/lib64"
                            }
                        },
                        # flags = maybe_flags
                    )
                ],
            )
        elif compiler == "gcc":
            cfg = compiler_section_for(
                "gcc",
                [
                    compiler_def(
                        "gcc@14.3.0 languages:=c,c++,fortran",
                        "/vol0500/share/ra250029/spack/opt/spack/a64fx/gcc-14.3.0",
                        {"c": "gcc", "cxx": "g++", "fortran": "gfortran"},
                        #                        env={
                        #                            "set": {
                        #                                "OPAL_PREFIX": "/vol0004/apps/oss/mpigcc/fjmpi-gcc12"
                        #                            },
                        #                            "append_path": {
                        #                                "LD_LIBRARY_PATH": "/opt/FJSVxtclanga/tcsds-1.2.42/lib64"
                        #                            },
                        #                        },
                        #                        flags={"ldflags": "-lelf -ldl"},
                    )
                ],
            )
        elif compiler == "fj":
            cfg = compiler_section_for(
                "fj",
                [
                    compiler_def(
                        "fj@4.12.2",
                        "/opt/FJSVxtclanga/tcsds-1.2.43/",
                        {"c": "fcc", "cxx": "FCC", "fortran": "frt"},
                        env={
                            "set": {
                                "fcc_ENV": "-Nclang",
                                "FCC_ENV": "-Nclang",
                            },
                            "prepend_path": {
                                "PATH": "/opt/FJSVxtclanga/tcsds-1.2.43/bin",
                                "LD_LIBRARY_PATH": "/opt/FJSVxtclanga/tcsds-1.2.43/lib64",
                            },
                        },
                    )
                ],
            )

        return cfg

    def system_specific_variables(self):
        return {
            "queue": "small",
            "extra_cmd_opts": "-std-proc fjmpioutdir/bmexe\n",
            "extra_batch_opts": '-x PJM_LLIO_GFSCACHE="/vol0002:/vol0003:/vol0004:/vol0005:/vol0006"\n',
            # Standard output of a run reaches one of two locations,
            # depending on whether ramble constructs the launch line.
            #
            # `extra_cmd_opts` adds `-std-proc fjmpioutdir/bmexe`, which
            # ramble appends only to executables declared `use_mpi=True`.
            # For those, output is written under fjmpioutdir/. An
            # application that builds its own launch line with
            # `use_mpi=False` does not receive the option, and the Fujitsu
            # MPI launcher then uses its default location,
            # output.<jobid>/<node>/<rank>/stdout.<n>.
            #
            # Collecting only the first location leaves the log empty for
            # the second case, so a success criterion matching text that
            # the application did print is not satisfied, and the run is
            # recorded as failed despite every exit code being zero.
            #
            # Both loops tolerate a missing directory, since an experiment
            # uses one location or the other.
            "post_exec_cmds": (
                "for F in $(ls -1v fjmpioutdir/bmexe.* 2>/dev/null); do cat $F >> {log_file}; done\n"
                "for F in $(ls -1v output.*/*/*/stdout.* 2>/dev/null); do cat $F >> {log_file}; done\n"
            ),
        }

    def compute_software_section(self):
        default_comp = self.spec.variants["compiler"][0]
        if default_comp == "clang":
            default_comp = "llvm"
        return {
            "software": {
                "packages": {
                    "default-compiler": {"pkg_spec": f"{default_comp}"},
                    "default-mpi": {"pkg_spec": "fujitsu-mpi"},
                    "compiler-clang": {"pkg_spec": "llvm"},
                    "compiler-fj": {"pkg_spec": "fj"},
                    "compiler-gcc": {"pkg_spec": "gcc"},
                    "blas": {"pkg_spec": "fujitsu-ssl2"},
                    "lapack": {"pkg_spec": "fujitsu-ssl2"},
                }
            }
        }
