# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import os
from spack.package import *
from spack_repo.builtin.packages.osu_micro_benchmarks.package import (
    OsuMicroBenchmarks as BuiltinOsu,
)

class OsuMicroBenchmarks(BuiltinOsu, ROCmPackage):

    patch("add-papi-option.patch", when="@7.5:")
    patch("add-papi-osu_util.patch", when="@7.5:")
    
    variant("managed", default=False, description="Enable CUDA managed memory support")

    depends_on("cray-mpich+gtl", when="+rocm")

    def configure_args(self):
        _base_args = super().configure_args()
    
        cuda_root = os.path.abspath(os.path.join(self.spec['cuda'].prefix, "..", ".."))
        #nvhpc_root = os.path.abspath(os.path.join(self.spec['nvhpc'].prefix, "..", ".."))
        mpi_root = self.spec['mpi'].prefix
        # ---------------------------------------------
        # --- デバッグ用：Spackが生成した生の引数を確認 ---
        #print("DEBUG: === Raw arguments from super() ===")
        #for i, arg in enumerate(_base_args):
        #    print(f"DEBUG: arg[{i}] = '{arg}'")
        # --- ついでにSpecの状態も確認 ---
        #if "+cuda" in self.spec:
        #    print(f"DEBUG: cuda prefix = '{self.spec['cuda'].prefix}'")
        #print(f"DEBUG: mpi_root    = '{mpi_root}'")
        #print(f"DEBUG: nvhpc_root  = '{nvhpc_root}'")
        #print(f"DEBUG: cuda_root   = '{cuda_root}'")
        #print("DEBUG: === Fin. ===")
        # ---------------------------------------------

        def pop_arg(name):
            for i, x in enumerate(_base_args):
                if x.startswith(f"{name}="):
                    return _base_args.pop(i).split('=', 1)[1]
            return ""

        def unique_list(seq):
            seen = set()
            return [x for x in seq if not (x in seen or seen.add(x))]

        old_cpp  = pop_arg("CPPFLAGS")
        old_ld   = pop_arg("LDFLAGS")
        old_libs = pop_arg("LIBS")

        mpi_lib    = os.path.join(self.spec['mpi'].prefix, "lib")
        extra_cpp  = []
        extra_ld   = [f"-L{mpi_lib}", f"-Wl,-rpath,{mpi_lib}"]
        extra_libs = []


        # --- 1. CUDA (+NVHPC) ---
        if self.spec.satisfies("+cuda"):
            _base_args = [a for a in _base_args if not a.startswith('--with-cuda=')]
            cuda_prefix = self.spec['cuda'].prefix
            _base_args.append(f"--with-cuda={cuda_prefix}")


            cuda_lib = os.path.join(cuda_prefix, "lib64")
            extra_ld.append(f"-L{cuda_lib}")
            cuda_stub_lib = os.path.join(cuda_lib, "stubs")
            if os.path.exists(cuda_stub_lib):
                extra_ld.append(f"-L{cuda_stub_lib}")
            extra_ld.append(f"-Wl,-rpath,{cuda_lib}")

            mpi_prefix = self.spec['mpi'].prefix
            comm_libs_root = os.path.abspath(os.path.join(mpi_prefix, "..", "..", ".."))

            # for NVSHMEM
            nvshmem_path = os.path.join(comm_libs_root, "nvshmem")
            if os.path.exists(nvshmem_path):
                link_cc = os.path.join(self.stage.source_path, "oshcc")
                link_cxx = os.path.join(self.stage.source_path, "oshc++")
                if not os.path.exists(link_cc):
                    os.symlink(self.spec['mpi'].mpicc, link_cc)
                if not os.path.exists(link_cxx):
                    os.symlink(self.spec['mpi'].mpicxx, link_cxx)

                _base_args = [a for a in _base_args if not a.startswith(('CC=', 'CXX='))]
                _base_args.append(f"CC={link_cc}")
                _base_args.append(f"CXX={link_cxx}")
                _base_args.append("enable_openshmem=yes")

                extra_cpp.append(f"-I{nvshmem_path}/include")
                extra_ld.append(f"-L{nvshmem_path}/lib")
                extra_libs.append("-lnvshmem")
                os.environ['SHMEM_HOME'] = nvshmem_path
            # CUDA library etc.
            extra_libs.extend(["-lcudart", "-lrt", "-lstdc++"])

            # for NCCL
            if self.spec.satisfies("+xccl"):
                _base_args = [a for a in _base_args if not a.startswith(('--enable-nccl', '--enable-rcclomb', '--with-nccl', '--with-rccl'))]
                nccl_prefix = os.path.join(comm_libs_root, "nccl")
                if os.path.exists(nccl_prefix):
                    _base_args.append("--enable-ncclomb")
                    _base_args.append(f"--with-nccl={nccl_prefix}")
                    extra_cpp.append(f"-I{nccl_prefix}/include")
                    extra_ld.append(f"-L{nccl_prefix}/lib")
                    extra_libs.append("-lnccl")

        # --- 2. ROCM ---
        elif self.spec.satisfies("+rocm"):
            extra_ld.append(self.spec['mpi'].libs.ld_flags)

            mpi_prefix = self.spec['mpi'].prefix
            if os.path.exists(os.path.join(mpi_prefix, "bin", "oshcc")):
                _base_args.append("enable_openshmem=yes")

            rccl_prefix = os.path.join(self.spec['rocm'].prefix, "rccl")
            if os.path.exists(rccl_prefix):
                _base_args.append("--enable-rccl")
                _base_args.append(f"--with-rccl={rccl_prefix}")
                extra_cpp.append(f"-I{rccl_prefix}/include")
                extra_ld.append(f"-L{rccl_prefix}/lib")
                extra_libs.append("-lrccl")

        # --- 3. CPU only (no CUDA/ROCM) ---
        elif self.spec.satisfies("~cuda") and self.spec.satisfies("~rocm"):
            mpi_prefix = self.spec['mpi'].prefix
            if os.path.exists(os.path.join(mpi_prefix, "bin", "oshcc")):
                _base_args.append("enable_openshmem=yes")
                _base_args = [a for a in _base_args if not a.startswith(('CC=', 'CXX='))]
                _base_args.append(f"CC={os.path.join(mpi_prefix, 'bin', 'oshcc')}")
                _base_args.append(f"CXX={os.path.join(mpi_prefix, 'bin', 'oshc++')}")

        if "+papi" in self.spec:
            papi_prefix = self.spec['papi'].prefix
            papi_inc = papi_prefix.include
            papi_lib = papi_prefix.lib

            _base_args.append(f"--enable-papi")
            _base_args.append(f"--with-papi={papi_prefix}")

            papi_flags = f"-I{papi_inc} -DPAPI -D_ENABLE_PAPI_=1"
            extra_cpp.append(papi_flags)
            extra_ld.extend([f"-L{papi_lib}", f"-Wl,-rpath,{papi_lib}"])
            extra_libs.append("-lpapi")

        # --- merge flag ---
        if old_cpp or extra_cpp:
            flags_str = f"{old_cpp} {' '.join(extra_cpp)}".strip()
            _base_args.append(f"CPPFLAGS={flags_str}")
            _base_args.append(f"CFLAGS={flags_str}")
        if old_ld or extra_ld:
            _base_args.append(f"LDFLAGS={old_ld} {' '.join(extra_ld)}".strip())
        if old_libs or extra_libs:
            _base_args.append(f"LIBS={old_libs} {' '.join(extra_libs)}".strip())

        _base_args = unique_list(_base_args)

        new_args = list()
        for x in _base_args:
            if "NVCCFLAGS" in x and self.spec.satisfies("%intel-oneapi-compilers"):
                new_args.append(x + " -allow-unsupported-compiler")
            else:
                new_args.append(x)

        # ---------------------------------------------
        #print("DEBUG: === New arguments ===")
        #for i, arg in enumerate(new_args):
        #    print(f"DEBUG: arg[{i}] = '{arg}'")
        #print("DEBUG: === Fin. ===")
        # ---------------------------------------------
        return new_args

    def setup_run_environment(self, env):
        mpidir = join_path(self.prefix.libexec, "osu-micro-benchmarks", "mpi")
        env.prepend_path("PATH", join_path(mpidir, "startup"))
        env.prepend_path("PATH", join_path(mpidir, "pt2pt"))
        env.prepend_path("PATH", join_path(mpidir, "one-sided"))
        env.prepend_path("PATH", join_path(mpidir, "collective"))
        env.prepend_path("PATH", join_path(mpidir, "congestion"))
        if self.spec.satisfies("+rocm"):
            if 'gtl_flags' in self.spec['mpi'].extra_attributes:
                env.prepend_path("LOCAL_RANK", self.spec['mpi'].extra_attributes['gtl_flags'])
        xccldir = join_path(self.prefix.libexec, "osu-micro-benchmarks", "xccl")
        env.prepend_path("PATH", join_path(xccldir, "collective"))
        env.prepend_path("PATH", join_path(xccldir, "pt2pt"))
        oshmdir = join_path(self.prefix.libexec, "osu-micro-benchmarks", "openshmem")
        env.prepend_path("PATH", join_path(oshmdir))

    #def patch(self):
    #    import time
    #    ###############################################################################
    #    # Forces the building of binaries that require MPI4.
    #    # Linking errors will occur if the MPI4 library is not present.
    #    ###############################################################################
    #    filter_file(r'SUBDIRS = neighborhood blocking non_blocking',
    #                'SUBDIRS = neighborhood blocking non_blocking persistent',
    #                'c/mpi/collective/Makefile.am')
    #    time.sleep(1)
    #    filter_file(r'SUBDIRS = neighborhood blocking non_blocking',
    #                'SUBDIRS = neighborhood blocking non_blocking persistent',
    #                'c/mpi/collective/Makefile.in')


    def configure(self, spec, prefix):
        # execute configure and create Makefile
        super().configure(spec, prefix)

        # modify Makefile 
        #print("DEBUG: =========================================")
        #print("DEBUG: Post-configure Makefile patching started")

        if "+papi" in spec:
            oshm_dir = os.path.join(self.stage.source_path, 'c', 'openshmem')
            oshm_makefile = os.path.join(oshm_dir, 'Makefile')

            if os.path.exists(oshm_makefile):
                #print(f"DEBUG: Found Makefile at {oshm_makefile}")

                filter_file(r'\.\./util/osu_util\.', 'osu_util_oshm.', oshm_makefile)
                filter_file(r'-DPAPI', '', oshm_makefile)
                filter_file(r'-D_ENABLE_PAPI_', '', oshm_makefile)

                with open(oshm_makefile, 'a') as f:
                    f.write('\n# Custom rule for OSHM\n')
                    f.write('osu_util_oshm.o: ../util/osu_util.c\n')
                    f.write('\t$(CC) $(DEFS) $(DEFAULT_INCLUDES) $(INCLUDES) $(AM_CPPFLAGS) $(CPPFLAGS) $(AM_CFLAGS) $(CFLAGS) -c -o $@ $<\n')

            #    print("DEBUG: Patching completed successfully")
            #else:
            #    print(f"DEBUG: ERROR - Makefile NOT FOUND at {oshm_makefile}")

        #print("DEBUG: =========================================")
