# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from benchpark.directives import maintainers, variant
from benchpark.error import BenchparkError
from benchpark.experiment import Experiment
from benchpark.programming_model import ProgrammingModel, ProgrammingModelType


class UcxPerftest(
    Experiment,
    ProgrammingModel(ProgrammingModelType.Cuda),
):
    """ucx_perftest, UCX's own point-to-point benchmark, between one server
    rank and one client rank on two nodes. The binary comes with spack's ucx
    package (a system may declare its MPI's UCX as an external); there is no
    package of its own.
    """

    variant(
        "workload",
        default="ucx_perftest",
        values=("ucx_perftest",),
        description="ucx_perftest benchmark",
    )

    variant(
        "version",
        default="latest",
        values=("latest", "master", "1.19.0", "1.20.0", "1.21.0", "1.22.0"),
        description="UCX version",
    )

    # Build options, named as spack's ucx names them
    variant("verbs", default=False, description="Build OpenFabrics support")
    variant("rc", default=False, description="Compile with IB Reliable Connection support")
    variant("ud", default=False, description="Compile with IB Unreliable Datagram support")
    variant("dc", default=False, description="Compile with IB Dynamic Connection support")
    variant("ib_hw_tm", default=False, description="Compile with IB Tag Matching support")
    variant("rdmacm", default=False, description="Enable the use of RDMACM")
    variant("mlx5", default=False, description="Compile with mlx5 Direct Verbs support (spack: mlx5_dv)")

    # ucx_perftest options (ucx_perftest -h). "undef" leaves the default.
    # Common
    variant("test", default="undef", description="Test to run (-t)")
    variant("msg_size", default="undef", description="Scatter-gather sizes of one message (-s)", multi=True)
    variant("mem_type", default="undef", description="Memory type of sender and receiver buffers (-m <send>[,<recv>])", multi=True)
    variant("iters", default="undef", description="Iterations (-n)")
    variant("warmup", default="undef", description="Warm-up iterations (-w)")
    variant("cpu_server", default="0", description="CPU the server is pinned to (-c)")
    variant("cpu_client", default="1", description="CPU the client is pinned to (-c)")
    variant("outstand", default="undef", description="Maximal number of outstanding sends (-O)")
    variant("distance", default="undef", description="Distance between scatter-gather entries (-i)")
    variant("no_progress", default="undef", description="Do not progress the responder in one-sided tests (-o)")
    variant("nonblock", default="undef", description="Register memory with NONBLOCK flag (-B)")
    variant("batchfile", default="undef", description="Read and execute tests from a batch file (-b)")
    variant("percentile_rank", default="undef", description="Percentile rank reported in latency tests (-R)")
    variant("TCPport", default="undef", description="TCP port for the data exchange (-p)")
    variant("ipv6", default="undef", description="Use an IPv6 address for the data exchange (-6)")
    # Output
    variant("numeric", default="undef", description="Numeric formatting with thousands separator (-N)")
    variant("final", default="undef", description="Print only the final numbers (-f)")
    variant("csv", default="undef", description="CSV output (-v)")
    variant("extra_info", default="undef", description="Extra information about the operation (-I)")
    variant("quiet", default="undef", description="Do not print error messages (-q)")
    # UCT only
    variant("device", default="undef", description="(UCT) device to test (-d)")
    variant("trans", default="undef", description="(UCT) transport to test (-x)")
    variant("layout", default="undef", description="(UCT) data layout on the sender (-D)", multi=True)
    variant("am_flow_size", default="undef", description="(UCT) flow-control window for active messages (-W)")
    variant("am_header", default="undef", description="(UCT) active message header size (-H)")
    variant("async_mode", default="undef", description="(UCT) asynchronous progress mode (-A)")
    # UCP only
    variant("threads", default="undef", description="(UCP) threads in the test (-T <threads>[:<blocks>])")
    variant("thread_level", default="undef", description="(UCP) thread support level (-M)")
    variant("wildcard", default="undef", description="(UCP) wild-card tag in tag tests (-C)")
    variant("force_unexpected", default="undef", description="(UCP) force the unexpected path with tag probe (-U)")
    variant("recv_mode", default="undef", description="(UCP) receive mode for stream tests (-r)")
    variant("error_handling", default="undef", description="(UCP) endpoints with error handling (-e)")
    variant("wait_mode", default="undef", description="(UCP) wait mode (-E)")
    variant("am_memcopy", default="undef", description="(UCP) extra memcopy in the active message handler (-y)")
    variant("prereg", default="undef", description="(UCP) pass pre-registered memory handles (-z)")
    variant("local_daemon", default="undef", description="(UCP) local daemon to offload to, IP[:port] (-g)")
    variant("remote_daemon", default="undef", description="(UCP) remote daemon to offload to, IP[:port] (-G)")

    # UCP tests take their transport and devices from the environment
    variant("UCX_TLS", default="all", description="UCX transports", multi=True)
    variant("UCX_SELF_DEVICES", default="all", description="UCX loopback devices", multi=True)
    variant("UCX_SHM_DEVICES", default="all", description="UCX shared-memory devices", multi=True)
    variant("UCX_NET_DEVICES", default="all", description="UCX network devices", multi=True)

    maintainers("nhanford")

    # options taking a value: (variant, flag)
    options_map = [
        ("test", "-t"),
        ("msg_size", "-s"),
        ("mem_type", "-m"),
        ("iters", "-n"),
        ("warmup", "-w"),
        ("outstand", "-O"),
        ("distance", "-i"),
        ("batchfile", "-b"),
        ("percentile_rank", "-R"),
        ("TCPport", "-p"),
        ("layout", "-D"),
        ("am_flow_size", "-W"),
        ("am_header", "-H"),
        ("async_mode", "-A"),
        ("threads", "-T"),
        ("thread_level", "-M"),
        ("recv_mode", "-r"),
        ("wait_mode", "-E"),
        ("local_daemon", "-g"),
        ("remote_daemon", "-G"),
    ]
    # options that are flags: (variant, flag)
    flags_map = [
        ("no_progress", "-o"),
        ("nonblock", "-B"),
        ("ipv6", "-6"),
        ("numeric", "-N"),
        ("final", "-f"),
        ("csv", "-v"),
        ("extra_info", "-I"),
        ("quiet", "-q"),
        ("wildcard", "-C"),
        ("force_unexpected", "-U"),
        ("error_handling", "-e"),
        ("am_memcopy", "-y"),
        ("prereg", "-z"),
    ]
    # options both sides take (the server only listens, but on that device
    # and transport): (variant, flag)
    server_options = [
        ("device", "-d"),
        ("trans", "-x"),
    ]

    def variant_value(self, name):
        value = self.spec.variants[name]
        if isinstance(value, (tuple, list)):
            return ",".join(str(x) for x in value)
        return str(value)

    def compute_applications_section(self):
        server_opts = [f"-c {self.variant_value('cpu_server')}"]
        client_opts = [f"-c {self.variant_value('cpu_client')}"]
        for name, flag in self.server_options:
            value = self.variant_value(name)
            if value != "undef":
                server_opts.append(f"{flag} {value}")
                client_opts.append(f"{flag} {value}")
        for name, flag in self.options_map:
            value = self.variant_value(name)
            if value != "undef":
                client_opts.append(f"{flag} {value}")
        for name, flag in self.flags_map:
            if self.variant_value(name).lower() == "true":
                client_opts.append(flag)

        self.add_experiment_variable("server_opts", " ".join(server_opts), False)
        self.add_experiment_variable("client_opts", " ".join(client_opts), False)
        for name in ("UCX_TLS", "UCX_SELF_DEVICES", "UCX_SHM_DEVICES", "UCX_NET_DEVICES"):
            self.add_experiment_variable(name, self.variant_value(name), False)

        # One server and one client, a node each. A GPU per node when the
        # test may touch device memory, so that the two steps find one.
        self.add_experiment_variable("n_nodes", 2, True)
        self.add_experiment_variable("n_ranks", 2, True)
        if self.spec.satisfies("+cuda"):
            self.add_experiment_variable("n_gpus", 2, True)
            self.add_experiment_variable("step_opts", "--gpus 1", False)
        self.set_required_variables(
            n_resources="{n_ranks}", process_problem_size="", total_problem_size=""
        )

    def compute_package_section(self):
        spec = f"ucx{self.determine_version()}"
        for name, spack_name in [
            ("verbs", "verbs"),
            ("rc", "rc"),
            ("ud", "ud"),
            ("dc", "dc"),
            ("ib_hw_tm", "ib_hw_tm"),
            ("rdmacm", "rdmacm"),
            ("mlx5", "mlx5_dv"),
        ]:
            if self.spec.satisfies(f"+{name}"):
                spec += f"+{spack_name}"
        self.add_package_spec(self.name, [spec])
