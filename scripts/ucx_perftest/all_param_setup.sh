#!/bin/bash

#test case
TEST_CASE="test=tag_lat msg_size=16,48"                 ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=tag_lat mem_type=cuda,cuda iters=10000" ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=tag_lat iters=999999"                   ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=tag_lat warmup=5000"                    ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=tag_lat outstand=16"                    ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=tag_lat distance=64"                    ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=put_lat no_progress=True device=mlx5_0:1 trans=rc_mlx5 " ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=tag_lat nonblock=True"                  ; sbatch setup.sh ${TEST_CASE}
  TEST_CASE="test=tag_lat batchfile=batchfile.txt"        ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=tag_lat percentile_rank=99.0"           ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=tag_lat TCPport=13337"                  ; sbatch setup.sh ${TEST_CASE}
  TEST_CASE="test=tag_lat ipv6=True"                      ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=tag_lat numeric=True"                   ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=tag_lat final=True"                     ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=tag_lat csv=True"                       ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=tag_lat extra_info=True"                ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=tag_lat quiet=True"                     ; sbatch setup.sh ${TEST_CASE}

#UCT only
TEST_CASE="test=am_lat device=mlx5_0:1 trans=rc_mlx5 am_flow_size=32"                        ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=am_lat device=mlx5_0:1 trans=rc_mlx5 am_header=4 msg_size=2046 layout=bcopy" ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=am_lat device=mlx5_0:1 trans=rc_mlx5 async_mode=thread_mutex"                ; sbatch setup.sh ${TEST_CASE}

#UCP only
TEST_CASE="test=tag_lat threads=2"                ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=tag_lat thread_level=serialized"  ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=tag_lat wildcard=True"            ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=tag_lat force_unexpected=True"    ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=tag_lat recv_mode=recv_data"      ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=tag_lat error_handling=True"      ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=tag_lat wait_mode=sleep"          ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=ucp_am_lat am_memcopy=True"       ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=tag_lat prereg=True"              ; sbatch setup.sh ${TEST_CASE}
  TEST_CASE="test=tag_lat local_daemon=127.0.0.1"   ; sbatch setup.sh ${TEST_CASE}
  TEST_CASE="test=tag_lat remote_daemon=127.0.0.1"  ; sbatch setup.sh ${TEST_CASE}

#
TEST_CASE="test=tag_lat UCX_TLS=rc,ud"                                                       ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=am_lat device=mlx5_0:1 trans=rc_mlx5 UCX_TLS=rc,ud UCX_NET_DEVICES=mlx5_0:1" ; sbatch setup.sh ${TEST_CASE}


