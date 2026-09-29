富岳で saxpy をセットアップする事例。
---
benchparkのcloneから実行/分析までの一連の流れ。\
富岳ログインノードで以下を実行する。\
python は、`python@3.10` 以上であること。
```bash
git clone https://github.com/RIKEN-RCCS/benchpark
cd benchpark
git checkout FN_apps 
python -m venv .venv_login
source .venv_login/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install .[analyze]
deactivate
pjsub --interact -L "node=1" -L "rscgrp=int" -L "elapse=1:00:00" --sparam "wait-time=300" --all-mount-gfscache
python -m venv .venv_fugaku
source .venv_fugaku/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install .[analyze]
deactivate
exit
# 上記のvenv作成は、git clone 後、1回だけ実行すればよい
# venv作成後は、以下を繰り返すことができる

pjsub --interact -L "node=1" -L "rscgrp=int" -L "elapse=6:00:00" --sparam "wait-time=300" --all-mount-gfscache
source .venv_fugaku/bin/activate
source ./setup-env.sh
source ./workspace/setup.sh
benchpark system init --dest=fugaku riken-fugaku compiler=fj
benchpark experiment init fugaku saxpy
benchpark setup fugaku/saxpy workspace
ramble --workspace-dir ./workspace/fugaku/saxpy/workspace workspace setup
deactivate
exit
source .venv_login/bin/activate
source ./setup-env.sh
source ./workspace/setup.sh
ramble --workspace-dir ./workspace/fugaku/saxpy/workspace on
# ジョブが終了するまで待つ
ramble --workspace-dir ./workspace/fugaku/saxpy/workspace workspace analyze
```
---
cloneおよびvenv作成は初回の1回のみ。venv作成後は、benchparkコマンドとrambleコマンドを繰り返し実行できる。\
venvは、作成した機種と実行する機種が異なると、エラーになる場合がある。\
そのため、１つのターミナルで操作する場合は、ログインノードと計算ノードで、venvを切り換える。\
ログインノード用のターミナルと計算ノード用のターミナルをそれぞれ開くと、venv切り換えの手間を省ける。
