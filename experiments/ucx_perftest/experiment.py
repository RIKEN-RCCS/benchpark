# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from benchpark.directives import maintainers, variant
from benchpark.experiment import Experiment
from benchpark.cuda import CudaExperiment


class UcxPerftest(Experiment, CudaExperiment):
    variant(
        "workload",
        default="ucx_perftest",
        values=("ucx_perftest", "ucx_perftesti_daemon"),
        description="ucx_perf_test benchmark",
    )

    variant(
        "version",
        default="master",
        values=("master", "1.19.0"),
        description="UCX version",
    )

    variant("cuda", default=False, description="Build with CUDA")
    variant("verbs", default=False, description="Build OpenFabrics support")
    variant("rc", default=False, description="Compile with IB Reliable Connection support")
    variant("ud", default=False, description="Compile with IB Unreliable Datagram support")
    variant("dc", default=False, description="Compile with IB Dynamic Connection support")
    variant("ib_hw_tm", default=False, description="Compile with IB Tag Matching support")
    variant("rdmacm", default=False, description="Enable the use of RDMACM")
    variant("mlx5", default=False, description="Compile with mlx5 Direct Verbs support")

    ###  ucx_perftest option list (ucx_perftest -h) :
    ## Common options:
    variant("test", default="undef", description="test to run (-t <test>)")
    #variant("accel_device", default="undef", description="Accelerator device type and device id to use for running the test (-a <device-type>[,<devce-type>] )", multi=True)
    #variant("device_level", default="undef", description="device cooperation level for gdaki (-L <level>)")
    #variant("flow_size", default="undef", description="flow control window size for device tests (-F <size>)")
    #variant("channel_mode", default="undef", description="channel selection mode for device tests (-Y <mode>)")
    variant("msg_size", default="undef", description="list of scatter-gather sizes for single message (-s <size>)", multi=True)
    variant("mem_type", default="undef", description="memory type of message for sender and recieve (-m <send mem type>[,<recv mem type>])", multi=True)
    variant("iters", default="undef", description="number of iterations to run (-n <iters>)")
    variant("warmup", default="undef", description="number of warm-up iterations (-w <iters>)")
    variant("cpu_server", default="0", description="set affinity for server (-c <cpulist>)")
    variant("cpu_client", default="1", description="set affinity for client (-c <cpulist>)")
    variant("outstand", default="undef", description="maximal number of uncompleted outstanding sends (-O <count>)")
    variant("distance", default="undef", description="distance between consecutive scatter-gather entries (-i <offset>)")
    # -l : use loopback connection
    variant("no_progress", default="undef", description="do not progress the responder in one-sided tests (-o)")
    variant("nonblock", default="undef", description="register memory with NONBLOCK flag (-B)")
    variant("batchfile", default="undef", description="read and execute tests from a batch file (-b <file>")
    variant("percentile_rank", default="undef", description="percentile rank of the percentile data in latency tests (-R <rank>)")
    variant("TCPport", default="undef", description="TCP port to use for data exchange (-p <port>)")
    variant("ipv6", default="undef", description="Use IPv6 address for in data exchange (-6)")
    # -K <ca:port> : use MAD for test setup and synchronization
    #                    MAD : Management Datagram is a packet used in Infiniband
    # -h : show this help message
    ## Output format:
    variant("numeric", default="undef", description="use numeric formatting (thousands separator) (-N)")
    variant("final", default="undef", description="print only final numbers (-f)")
    variant("csv", default="undef", description="print CSV-formatted output (-v)")
    variant("extra_info", default="undef", description="print extra information about the operation (-I)")
    variant("quiet", default="undef", description="do not print error messages (-q)")
    ## UCT only:
    variant("device", default="undef", description="(UCT only) device to use for testing (-d <device>)")
    variant("trans", default="undef", description="(UCT only) transport to use for testing (-x <tl>)")
    variant("layout", default="undef", description="(UCT only) data layout for sender side (-D <layout>)", multi=True)
    variant("am_flow_size", default="undef", description="(UCT only) flow control window size, for active messages (-W <count>)")
    variant("am_header", default="undef", description="(UCT only) active message header size, included in message size (-H <size>)")
    variant("async_mode", default="undef", description="(UCT only) asynchronous progress mode (-A <mode>)")
    ## UCP only:
    variant("threads", default="undef", description="(UCP only) number of threads in the test (-T <threads>[:<blocks>])")
    variant("thread_level", default="undef", description="(UCP only) thread support level for progress engine (-M <thread>)")
    ####variant("layout", default="undef", description="(UCP only) data layout for sender and receiver side (-D <layout>[,<layout>])", multi=True)
    variant("wildcard", default="undef", description="(UCP only) use wild-card tag for tag tests (-C)")
    variant("force_unexpected", default="undef", description="(UCP only) force unexpected flow by using tag probe (-U)")
    variant("recv_mode", default="undef", description="(UCP only) receive mode for stream tests (-r <mode>)")
    #variant("wakeup", default="undef", description="(UCP only) create context with wakeup feature enabled (-I)")
    variant("error_handling", default="undef", description="(UCP only) create endpoints with error handling support (-e)")
    variant("wait_mode", default="undef", description="(UCP only) wait mode for tests (-E <mode>)")
    ####variant("am_header", default="undef", description="(UCP only) active message header size, not included in message size (-H <size>)")
    variant("am_memcopy", default="undef", description="(UCP only) do additional memcopy to the user memory in active message receive handler (-y)")
    variant("prereg", default="undef", description="(UCP only) pass pre-registered memory handle (-z)")
    variant("local_daemon", default="undef", description="(UCP only) IP address and port of the local daemon to offload UCP operations to (-g <IP>[:<port>])")
    variant("remote_daemon", default="undef", description="(UCP only) IP address and port of the remote daemon to offload UCP operations to (-G <IP>[:<port>])")

    #   NOTE: When running UCP tests, transport and device should be specified by
    #         environment variables: UCX_TLS and UCX_[SELF|SHM|NET]_DEVICES.
    variant("UCX_TLS", default="all", description="UCX Transport Layer", multi=True)
    variant("UCX_SELF_DEVICES", default="all", description="UCX Network Devices", multi=True)
    variant("UCX_SHM_DEVICES", default="all", description="UCX Network Devices", multi=True)
    variant("UCX_NET_DEVICES", default="all", description="UCX Network Devices", multi=True)

    def compute_applications_section(self):
        import yaml
        import os
        import sys

        # --- module load ---
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
                # get nvhpc externals
                nvhpc_externals = data.get('packages', {}).get('nvhpc', {}).get('externals', [])
                if nvhpc_externals:
                    modules = nvhpc_externals[0].get('modules', [])

        setup_env_cmd = "echo ''; "
        for m in modules:
            setup_env_cmd += f"module load {m};"
        self.add_experiment_variable("pre_run_cmds", setup_env_cmd, False)


        # --- ---
        self.add_experiment_variable("n_nodes", 2)
        self.set_required_variables(
            n_resources="{n_nodes}", process_problem_size="", total_problem_size=""
        )

        def get_val(name):
            val = self.spec.variants[name]
            if isinstance(val, (tuple, list)):
                return ",".join(map(str, val))
            return str(val)

        options_map = {
            "cpu_server": "-c",
            "cpu_client": "-c",
            "test": "-t",
            #"accel_device": "-a",
            #"device_level": "-L",
            #"flow_size": "-F",
            #"channel_mode": "-Y",
            "msg_size": "-s",
            "mem_type": "-m",
            "iters": "-n",
            "warmup": "-w",
            "outstand": "-O",
            "distance": "-i",
            "batchfile": "-b",
            "percentile_rank": "-R",
            "TCPport": "-p",
            "device": "-d",
            "trans": "-x",
            "layout": "-D",
            "am_flow_size": "-W",
            "am_header": "-H",
            "async_mode": "-A",
            "threads": "-T",
            "thread_level": "-M",
            "recv_mode": "-r",
            "wait_mode": "-E",
            "local_daemon": "-g",
            "remote_daemon": "-G",
        }
        flags_map = {
            "no_progress": "-o",
            "nonblock": "-B",
            "ipv6": "-6",
            "numeric": "-N",
            "final": "-f",
            "csv": "-v",
            "extra_info": "-I",
            "quiet": "-q",
            "wildcard": "-C",
            "force_unexpected": "-U",
            #"wakeup": "-I",
            "error_handling": "-e",
            "am_memcopy": "-y",
            "prereg": "-z",
        }

        s_opts = []
        c_opts = []
        for var_name, flag in options_map.items():
            val = get_val(var_name)
            if var_name == "cpu_server" or var_name == "cpu_client":
                if var_name == "cpu_server":
                    s_opts.append(f"{flag} {val}")
            if var_name == "device" or var_name == "trans":
                if val != "undef" and val != "":
                    s_opts.append(f"{flag} {val}")
        for var_name, flag in options_map.items():
            val = get_val(var_name)
            if var_name == "cpu_server" or var_name == "cpu_client":
                if var_name == "cpu_client":
                    c_opts.append(f"{flag} {val}")
            elif val != "undef" and val != "":
                c_opts.append(f"{flag} {val}")
        for var_name, flag in flags_map.items():
            val = get_val(var_name)
            if val == "True" or val == "true":
                c_opts.append(flag)

        server_opts = " ".join(s_opts)
        client_opts = " ".join(c_opts)

        self.add_experiment_variable("client_opts", client_opts)
        self.add_experiment_variable("server_opts", server_opts)
        self.add_experiment_variable("UCX_TLS", get_val("UCX_TLS"))
        self.add_experiment_variable("UCX_SELF_DEVICES", get_val("UCX_SELF_DEVICES"))
        self.add_experiment_variable("UCX_SHM_DEVICES", get_val("UCX_SHM_DEVICES"))
        self.add_experiment_variable("UCX_NET_DEVICES", get_val("UCX_NET_DEVICES"))


    def compute_package_section(self):
        spec = "ucx_perftest"

        if self.spec.satisfies("+verbs"):
            spec += "+verbs"
        if self.spec.satisfies("+rc"):
            spec += "+rc"
        if self.spec.satisfies("+ud"):
            spec += "+ud"
        if self.spec.satisfies("+dc"):
            spec += "+dc"
        if self.spec.satisfies("+ib_hw_tm"):
            spec += "+ib_hw_tm"
        if self.spec.satisfies("+rdmacm"):
            spec += "+rdmacm"
        if self.spec.satisfies("+mlx5"):
            spec += "+mlx5"

        self.add_package_spec(self.name, [spec])
