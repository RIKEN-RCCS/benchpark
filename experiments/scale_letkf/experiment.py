from benchpark.directives import variant
from benchpark.experiment import Experiment
from benchpark.programming_model import ProgrammingModel, ProgrammingModelType

class ScaleLetkf(
    Experiment,
    ProgrammingModel(
        ProgrammingModelType.Mpionly,
    ),
):

    variant(
        "workload",
        default="benchmark",
        description="Which ramble workload to execute.",
    )

    variant(
        "cluster",
        default="unknown",
        values=("fugaku", "fx700", "genoa", "gh200", "unknown"),
        description="Target cluster system"
    )

    variant(
        "compiler",
        default="unknown",
        values=("gcc", "fj", "nvhpc", "unknown"),
        description="Target compiler to use"
    )

    def compute_applications_section(self):
        cluster = self.spec.variants["cluster"][0]
        tuning_cmds = "export OMP_WAIT_POLICY=active; ulimit -s unlimited"

        if cluster =="fugaku":
            self.add_experiment_variable("n_nodes", ["3"], True)
            self.add_experiment_variable("processes_per_node", ["4"], True)
            self.add_experiment_variable("omp_num_threads", ["10"], True)
            self.add_experiment_variable("archives_path", "/vol0500/share/ra250029/CX_input/SCALE-LETKF", False)
            self.add_experiment_variable("extra_batch_opts", "-g ra250029 -x PJM_LLIO_GFSCACHE=/vol0004:/vol0005", False)
            tuning_cmds += "; export FORT90L=-Wl,-T; export PLE_MPI_STD_EMPTYFILE=off"
        elif cluster == "fx700":
            self.add_experiment_variable("n_nodes", ["3"], True)
            self.add_experiment_variable("processes_per_node", ["4"], True)
            self.add_experiment_variable("omp_num_threads", ["10"], True)
            self.add_experiment_variable("archives_path", "/lvs0/rccs-nghpcadu/CX_input/SCALE-LETKF", False)
            self.add_experiment_variable("extra_batch_opts", "-N {n_nodes} -c {omp_num_threads}", False)
            tuning_cmds += "; export FORT90L=-Wl,-T; export PLE_MPI_STD_EMPTYFILE=off"
        elif cluster == "gh200":
            self.add_experiment_variable("n_nodes", ["1"], True)
            self.add_experiment_variable("processes_per_node", ["12"], True)
            self.add_experiment_variable("omp_num_threads", ["1"], True)
            self.add_experiment_variable("archives_path", "/lvs0/rccs-nghpcadu/CX_input/SCALE-LETKF", False)
            self.add_experiment_variable("extra_batch_opts", "-N {n_nodes} -c {omp_num_threads}", False)
        else:
            self.add_experiment_variable("n_nodes", ["1"], True)
            self.add_experiment_variable("processes_per_node", ["12"], True)
            self.add_experiment_variable("omp_num_threads", ["8"], True)
            self.add_experiment_variable("archives_path", "/lvs0/rccs-nghpcadu/CX_input/SCALE-LETKF", False)
            self.add_experiment_variable("extra_batch_opts", "-N {n_nodes} -c {omp_num_threads}", False)

        self.add_experiment_variable("n_ranks", ["12"], True)
        self.add_experiment_variable("pp_ranks", ["4"], True)
        self.add_experiment_variable("tuning_cmds", tuning_cmds, False)
        
        self.add_experiment_variable("date_str", "20210730060000", False)
        self.add_experiment_variable("letkf_date", "20210730060030", False)
        
        self.add_experiment_variable("pp_conf", "conf/scale-rm_pp_ens_{date_str}.conf", False)
        self.add_experiment_variable("init_conf", "conf/scale-rm_init_ens_{date_str}.conf", False)
        self.add_experiment_variable("run_conf", "conf/scale-rm_ens_{date_str}.conf", False)
        self.add_experiment_variable("letkf_conf", "conf/letkf_{letkf_date}.conf", False)

        self.add_experiment_variable("scale_database_path", "{archives_path}/scale_database.tar.gz", False)
        self.add_experiment_variable("dataset_path", "{archives_path}/SCALE-LETKF.dataset-SC23.part1.20240410.tar.gz", False)

        self.add_experiment_variable("benchmark_dir", "benchmark.RC_GH200_128x128", False)
        self.add_experiment_variable("size", "128 * 128", True)

        self.set_required_variables(
            n_resources="{n_ranks}",
            process_problem_size="{size} / {n_ranks}", 
            total_problem_size="{size}",
        )

    def compute_package_section(self):
        compiler = self.spec.variants["compiler"][0]
        spec_str = "scale-letkf"

        if compiler == "gcc":
            spec_str += " %gcc ^openmpi %gcc"
        elif compiler == "nvhpc":
            spec_str += " %nvhpc ^openmpi %nvhpc"
        elif compiler == "fj":
            spec_str += " %fj"

        self.add_package_spec("scale_letkf", [spec_str])
