#!/bin/bash

#test case
TEST_CASE="test=am_lat  device=mlx5_0:1 trans=rc_mlx5"              ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=put_lat device=mlx5_0:1 trans=rc_mlx5"              ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=add_lat device=mlx5_0:1 trans=rc_mlx5"              ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=get     device=mlx5_0:1 trans=rc_mlx5 layout=bcopy" ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=fadd    device=mlx5_0:1 trans=rc_mlx5"              ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=swap    device=mlx5_0:1 trans=rc_mlx5"              ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=cswap   device=mlx5_0:1 trans=rc_mlx5"              ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=am_bw   device=mlx5_0:1 trans=rc_mlx5"              ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=put_bw  device=mlx5_0:1 trans=rc_mlx5"              ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=get_bw  device=mlx5_0:1 trans=rc_mlx5 layout=bcopy" ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=add_mr  device=mlx5_0:1 trans=rc_mlx5"              ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=tag_lat"      ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=tag_bw"       ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=tag_sync_lat" ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=tag_sync_bw"  ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=ucp_put_lat"  ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=ucp_put_bw"   ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=ucp_get"      ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=ucp_add"      ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=ucp_fadd"     ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=ucp_swap"     ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=ucp_cswap"    ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=stream_bw"    ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=stream_lat"   ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=ucp_am_lat"   ; sbatch setup.sh ${TEST_CASE}
TEST_CASE="test=ucp_am_bw"    ; sbatch setup.sh ${TEST_CASE}


