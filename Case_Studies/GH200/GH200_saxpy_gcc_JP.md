rccs-cloud の GH200 で saxpy をセットアップする事例。
---
benchparkのcloneから実行/分析までの一連の流れ。\
rccs-cloudのlogin1にログインした後、以下を実行する。\
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
srun -N 1 -p qc-gh200 --time=01:00:00 --pty bash
python -m venv .venv_gh200
source .venv_gh200/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install .[analyze]
deactivate
exit
# 上記のvenv作成は、git clone 後、1回だけ実行すればよい
# venv作成後は、以下を繰り返すことができる

source .venv_login/bin/activate
source ./setup-env.sh
benchpark system init --dest=gh200 riken-cloud cluster=gh200 compiler=gcc
benchpark experiment init gh200 saxpy
benchpark setup gh200/saxpy workspace
deactivate
srun -N 1 -p qc-gh200 --time=06:00:00 --pty bash
source .venv_gh200/bin/activate
source ./setup-env.sh
source ./workspace/setup.sh
ramble --workspace-dir ./workspace/gh200/saxpy/workspace workspace setup
deactivate
exit
source .venv_login/bin/activate
source ./setup-env.sh
source ./workspace/setup.sh
ramble --workspace-dir ./workspace/gh200/saxpy/workspace on
# ジョブが終わるまで待つ
ramble --workspace-dir ./workspace/gh200/saxpy/workspace workspace analyze
```
---
GH200 では、nvhpcを利用することができる。（バージョンは、25.9, 25.7, 24.9, 24.3 から選択できる）
```bash
benchpark system init --dest=gh200 riken-cloud cluster=gh200 compiler=nvhpc  ← デフォルトは nvhpc@25.7
benchpark system init --dest=gh200 riken-cloud cluster=gh200 compiler=nvhpc nvhpc=25.9  ← nvhpc@25.9 に変更する
```
---
cloneおよびvenv作成は初回の1回のみ。venv作成後は、benchparkコマンドとrambleコマンドを繰り返し実行できる。\
venvは、作成した機種と実行する機種が異なると、エラーになる場合がある。\
そのため、１つのターミナルで操作する場合は、機種変更の(srunを実行する)タイミングで、venvを切り換える。\
login1用のターミナルとgh200用のターミナルをそれぞれ開くと、venv切り換えの手間を省ける。
