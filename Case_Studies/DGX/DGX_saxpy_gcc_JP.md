rccs-cloud の DGX で saxpy をセットアップする事例。
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
srun -N 1 -p ng-dgx-3h --time=01:00:00 --pty bash
python -m venv .venv_dgx
source .venv_dgx/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install .[analyze]
deactivate
exit
# 上記のvenv作成は、git clone 後、1回だけ実行すればよい
# venv作成後は、以下を繰り返すことができる

source .venv_login/bin/activate
source ./setup-env.sh
benchpark system init --dest=dgx riken-cloud cluster=dgx compiler=gcc
benchpark experiment init dgx saxpy
benchpark setup dgx/saxpy workspace
deactivate
srun -N 1 -p ng-dgx-3h --time=06:00:00 --pty bash
source .venv_dgx/bin/activate
source ./setup-env.sh
source ./workspace/setup.sh
ramble --workspace-dir ./workspace/dgx/saxpy/workspace workspace setup
deactivate
exit
source .venv_login/bin/activate
source ./setup-env.sh
source ./workspace/setup.sh
ramble --workspace-dir ./workspace/dgx/saxpy/workspace on
# ジョブが終了するまで待つ
ramble --workspace-dir ./workspace/dgx/saxpy/workspace workspace analyze
```
---
DGX では、nvhpcを利用することができる。（バージョンは、26.3 のみ使用可能）
```bash
benchpark system init --dest=dgx riken-cloud cluster=dgx compiler=nvhpc  ← デフォルトで nvhpc@26.3 が設定される
```
---
cloneおよびvenv作成は初回の1回のみ。venv作成後は、benchparkコマンドとrambleコマンドを繰り返し実行できる。\
venvは、作成した機種と実行する機種が異なると、エラーになる場合がある。\
そのため、１つのターミナルで操作する場合は、毎回、venvを切り換える。\
login1用のターミナルとdgx用のターミナルをそれぞれ開くと、venv切り換えの手間を省ける。
