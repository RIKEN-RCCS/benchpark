from benchpark.experiment import Experiment
from benchpark.mpi import MpiOnlyExperiment
from benchpark.directives import variant, maintainers

class Ffb(Experiment, MpiOnlyExperiment):

  variant(
      "workload",
      default="cavity",
      description="ffb",
  )

  variant(
    "version",
    default="67.01",
    description="Which benchmark version to use.",
  )

  maintainers("ando")

  pre_cmds = [
       "module purge",
       "module load system/qc-gh200 nvhpc/24.3"
  ]

  def compute_applications_section(self):

    self.add_experiment_variable("n_nodes", 4, True)            # -N
    self.add_experiment_variable("processes_per_node", 1)
    self.add_experiment_variable("n_ranks", "{processes_per_node} * {n_nodes}")

    self.add_experiment_variable("Ns", 31255875, True)

    self.set_required_variables(
      n_resources="{n_ranks}",
      process_problem_size="{Ns}/{n_ranks}",
      total_problem_size="{Ns}",
    )

  def compute_package_section(self):
    self.add_package_spec(self.name, ["ffb@main"])
