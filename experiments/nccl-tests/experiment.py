from benchpark.cuda import CudaExperiment
from benchpark.directives import variant
from benchpark.experiment import Experiment
from benchpark.mpi import MpiOnlyExperiment

class NcclTests(
    Experiment,
    MpiOnlyExperiment,
    CudaExperiment,
):
    """NCCL Tests experiment class for GH200 (Benchpark style)"""
    name = "nccl-tests"

    variant(
        "workload",
        default="all-reduce",
        values=(
            "all-gather",
            "all-reduce",
            "all-to-all",
            "broadcast",
            "gather",
            "hypercube",
            "reduce",
            "reduce-scatter",
            "scatter",
            "send-recv",
        ),
        multi=True,
        description="workloads to run",
    )
    # variant for spack
    variant('mpi', default=True, description='Enable MPI support for NCCL tests')

    # variant for experiment
    variant('nprocs', default='2', description='Number of processes')
    #--------------------------------------------------------------------------------------------------
    # If not specified as an argument, the following parameters will use the default values for the Nccl test.
    #--------------------------------------------------------------------------------------------------
    # Number of GPUs
    variant('nthreads_proc', default='1', description='Number of threads per process(-t)')
    variant('ngpus_thread', default='1', description='Number of gpus per thread(-g)')
    # Sizes to scan
    variant('min_bytes', default='none', description='Beginning message size')
    variant('max_bytes', default='none', description='Ending message size')
    variant('step_inc', default='none', description="Message size increment (-i)")
    variant('step_factor', default='none', description='Factor used in size sweep (-f)')
    # NCCL operations arguments
    variant('op', default='none', description="Reduction operation <sum/prod/min/max/avg/all> (-o)")
    variant('datatype', default='none', description="Datatype to use <nccltype/all> (-d)")
    variant('root', default='none', description="Root rank  <root/all> (-r)")
    # Performance
    variant('num_iters', default='none', description='Number of iterations to perform (-n)')
    variant('warmup_iters', default='none', description='Number of warmup iterations (-w)')
    variant('agg_iters', default='none', description="Number of operations to aggregate together in each iteration (-m)")
    variant('run_cycles', default='none', description="Run and print each cycle.0=infinite(-N)")
    variant('average', default='none', description="Report performance as an average across all ranks  <0/1/2/3>  <0=Rank0,1=Avg,2=Min,3=Max> (-a)")
    # Test operation
    variant('parallel_init', default='none', description="use threads to initialize NCCL in parallel (-p)")
    variant('result_check', default='none', description='perform count iterations, checking correctness of results on each iteration (-c)')
    variant('blocking', default='none', description="Make NCCL collective blocking <0/1> (-z)")
    variant('cudagraph', default='none', description="Capture iterations as a CUDA graph and then replay specified number of times (-G)")
    variant('report_cputime', default='none', description="Report CPU time instead of latency <0/1>(-C)")
    variant('local_register', default='none', description="enable local (1) or symmetric (2) buffer registration on send/recv buffers <0/1/2>(-R)")
    variant('report_timestamps', default='none', description="Add timestamp to each performance report line <0/1> (-S)")
    variant('output_file', default='none', description="Write [JSON] output to filepath (-J)")
    variant('timeout', default='none', description="Timeout each test after specified number of seconds (-T)")
    # -M option does not exist in Nccl-Tests 2.7.16
    #variant('memory_report', default='none', description="Enable memory usage report (-M)")

    def calculate_resource_config(self):
        n_procs    = int(self.spec.variants['nprocs'][0])
        nthreads   = int(self.spec.variants['nthreads_proc'][0])
        ngpus_task = int(self.spec.variants['ngpus_thread'][0])

        system_obj = getattr(self.system_spec, 'system', None)

        sys_cores_per_node = int(getattr(system_obj, 'sys_cores_per_node', 1))
        if sys_cores_per_node < nthreads:
            raise Exception(
                f"Resource Error: The number of threads requested for one process ({nthreads}) "
                f"                exceeds the number of physical cores per node ({sys_cores_per_node})."
            )
        if self.spec.satisfies("+cuda"):
            sys_gpus_per_node = int(getattr(system_obj, 'sys_gpus_per_node', 1))
            need_gpus_per_process = nthreads * ngpus_task
            if sys_gpus_per_node < need_gpus_per_process:
                raise Exception(
                    f"Resource Error: The number of GPUs requested for one process ({need_gpus_per_process}) "
                    f"                exceeds the number of physical GPUs per node ({sys_gpus_per_node})."
                )
            ranks_per_node = sys_gpus_per_node // need_gpus_per_process
            total_gpus = n_procs * need_gpus_per_process
        else:
            ranks_per_node = sys_cores_per_node // nthreads
            total_gpus = 0

        n_nodes = (n_procs + ranks_per_node - 1) // ranks_per_node

        return n_nodes, total_gpus



    def compute_applications_section(self):
        import sys
        import os
        import yaml

        dest_dir = None
        for i, arg in enumerate(sys.argv):
            if arg == 'init' and i + 1 < len(sys.argv):
                dest_dir = sys.argv[i + 1]
                break

        if not dest_dir:
            return

        # read packages.yaml
        yaml_path = os.path.join(dest_dir, 'auxiliary_software_files', 'packages.yaml')
        modules = []
        if os.path.exists(yaml_path):
            with open(yaml_path, 'r') as f:
                data = yaml.safe_load(f)
                # get mpi externals
                mpi_externals = data.get('packages', {}).get('mpi', {}).get('externals', [])
                if mpi_externals:
                    modules = mpi_externals[0].get('modules', [])

        setup_env_cmd = "echo ''; "
        for m in modules:
            setup_env_cmd += f"module load {m};"
        self.add_experiment_variable("pre_run_cmds", setup_env_cmd, False)

        # setting all_options
        all_options = [
            ('nthreads_proc', '-t'), ('ngpus_thread', '-g'),
            ('min_bytes', '-b'),     ('max_bytes', '-e'),
            ('op', '-o'),            ('datatype', '-d'),
            ('root', '-r'),          ('num_iters', '-n'),
            ('warmup_iters', '-w'),  ('agg_iters', '-m'),
            ('run_cycles', '-N'),    ('average', '-a'),
            ('parallel_init', '-p'), ('result_check', '-c'),
            ('blocking', '-z'),      ('cudagraph', '-G'),
            ('report_cputime', '-C'), ('local_register', '-R'),
            ('report_timestamps', '-S'), ('output_file', '-J'),
            ('timeout', '-T'),   #('memory_report', '-M')
        ]
        add_args = ""
        for var_name, flag in all_options:
            val = self.spec.variants[var_name][0]
            if val != 'none':
                add_args += f" {flag} {val}"

        val_step_inc = self.spec.variants['step_inc'][0]
        val_step_factor = self.spec.variants['step_factor'][0]
        if val_step_factor != 'none' and val_step_inc != 'none':
            raise Exception("Error: 'step_inc' (-i) and 'step_factor' (-f) cannot be specified at the same time.")
        if val_step_inc != 'none':
            add_args += f" -i {val_step_inc}"
        if val_step_factor != 'none':
            add_args += f" -f {val_step_factor}"

        # check message size parameter
        val_max = self.spec.variants['max_bytes'][0]
        end_message_size = val_max if val_max != 'none' else '32M'

        n_nodes, total_gpus = self.calculate_resource_config()

        self.add_experiment_variable("n_nodes", n_nodes, True)
        if self.spec.satisfies("+cuda"):
            self.add_experiment_variable("n_gpus", total_gpus, True)
        resource_ref = "{n_procs}"

        self.set_required_variables(
            n_resources=resource_ref,
            process_problem_size="{end_message_size}",
            total_problem_size="{end_message_size}"
        )

        self.add_experiment_variable("additional_args", add_args, False)
        return {
            'nccl-tests': {
                'executables': ['{executable}'],
                'variables': {
                    'additional_args': add_args,
                }
            }
        }

    def compute_package_section(self):
        pkg_spec = 'nccl-tests'
        pkg_spec += '+mpi' if self.spec.satisfies('+mpi') else '~mpi'

        self.add_package_spec(self.name, [pkg_spec])

