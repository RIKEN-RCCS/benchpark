理研 の RIKYU で saxpy をセットアップする事例。
---
benchparkのcloneから実行/分析までの一連の流れ。\
RIKYUのloginノードにログインした後、以下を実行する。\
python は、`python@3.10` 以上であること。
```bash
git clone https://github.com/RIKEN-RCCS/benchpark
cd benchpark
git checkout FN_apps 
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install .[analyze]
#
# 上記のvenv作成は、git clone 後、1回だけ実行すればよい
# venv作成後は、以下を繰り返すことができる

source ./setup-env.sh
source ./workspace/setup.sh
benchpark system init --dest=rikyu riken-rikyu compiler=gcc
benchpark experiment init rikyu saxpy
benchpark setup rikyu/saxpy workspace
ramble --workspace-dir ./workspace/rikyu/saxpy/workspace workspace setup
ramble --workspace-dir ./workspace/rikyu/saxpy/workspace on
# ジョブが終わるまで待つ
ramble --workspace-dir ./workspace/rikyu/saxpy/workspace workspace analyze
```
---
RIKYU では、nvhpcを利用することができる。（バージョンは、26.5, 26,3, 25.11, 25.7, 24.9 から選択できる）
```bash
benchpark system init --dest=rikyu riken-rikyu compiler=nvhpc  ← デフォルトは nvhpc@26.5
benchpark system init --dest=rikyu riken-rikyu compiler=nvhpc nvhpc=25.7  ← nvhpc@25.7 に変更する
```
---
cloneおよびvenv作成は初回の1回のみ。venv作成後は、benchparkコマンドとrambleコマンドを繰り返し実行できる。
