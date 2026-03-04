#!/bin/bash

#test case
TEST_CASE="test=am_lat  device=mlx5_0:1 trans=rc_mlx5"              ; sh ./experiment.sh ${TEST_CASE}
TEST_CASE="test=put_lat device=mlx5_0:1 trans=rc_mlx5"              ; sh ./experiment.sh ${TEST_CASE}
TEST_CASE="test=add_lat device=mlx5_0:1 trans=rc_mlx5"              ; sh ./experiment.sh ${TEST_CASE}
TEST_CASE="test=get     device=mlx5_0:1 trans=rc_mlx5 layout=bcopy" ; sh ./experiment.sh ${TEST_CASE}
TEST_CASE="test=fadd    device=mlx5_0:1 trans=rc_mlx5"              ; sh ./experiment.sh ${TEST_CASE}
TEST_CASE="test=swap    device=mlx5_0:1 trans=rc_mlx5"              ; sh ./experiment.sh ${TEST_CASE}
TEST_CASE="test=cswap   device=mlx5_0:1 trans=rc_mlx5"              ; sh ./experiment.sh ${TEST_CASE}
TEST_CASE="test=am_bw   device=mlx5_0:1 trans=rc_mlx5"              ; sh ./experiment.sh ${TEST_CASE}
TEST_CASE="test=put_bw  device=mlx5_0:1 trans=rc_mlx5"              ; sh ./experiment.sh ${TEST_CASE}
TEST_CASE="test=get_bw  device=mlx5_0:1 trans=rc_mlx5 layout=bcopy" ; sh ./experiment.sh ${TEST_CASE}
TEST_CASE="test=add_mr  device=mlx5_0:1 trans=rc_mlx5"              ; sh ./experiment.sh ${TEST_CASE}
TEST_CASE="test=tag_lat"             ; sh ./experiment.sh ${TEST_CASE}
TEST_CASE="test=tag_bw"              ; sh ./experiment.sh ${TEST_CASE}
TEST_CASE="test=tag_sync_lat"        ; sh ./experiment.sh ${TEST_CASE}
TEST_CASE="test=tag_sync_bw"         ; sh ./experiment.sh ${TEST_CASE}
TEST_CASE="test=ucp_put_lat"         ; sh ./experiment.sh ${TEST_CASE}
TEST_CASE="test=ucp_put_bw"          ; sh ./experiment.sh ${TEST_CASE}
TEST_CASE="test=ucp_get"             ; sh ./experiment.sh ${TEST_CASE}
TEST_CASE="test=ucp_add"             ; sh ./experiment.sh ${TEST_CASE}
TEST_CASE="test=ucp_fadd"            ; sh ./experiment.sh ${TEST_CASE}
TEST_CASE="test=ucp_swap"            ; sh ./experiment.sh ${TEST_CASE}
TEST_CASE="test=ucp_cswap"           ; sh ./experiment.sh ${TEST_CASE}
TEST_CASE="test=stream_bw"           ; sh ./experiment.sh ${TEST_CASE}
TEST_CASE="test=stream_lat"          ; sh ./experiment.sh ${TEST_CASE}
TEST_CASE="test=ucp_am_lat"          ; sh ./experiment.sh ${TEST_CASE}
TEST_CASE="test=ucp_am_bw"           ; sh ./experiment.sh ${TEST_CASE}


