from spack.package import *
from spack_repo.builtin.packages.nccl_tests.package import (
    NcclTests as BuiltinNcclTests,
)

class NcclTests(BuiltinNcclTests):
    """GH200 optimized NCCL Tests (Inherited from Built-in via spack_repo)"""
    pass

