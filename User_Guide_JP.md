---

## 1. python環境の確認

pythonはV3.10以上が必要。以下でバージョンを確認し、
V3.10よりも低いバージョンの場合は、新たにpythonをインストールする。
```bash
python --version
```
---

## 2. benchparkのセットアップ
### 2.1 GitHubから環境をcloneする。
```bash
git clone https://github.com/RIKEN-RCCS/benchpark
```
### 2.2 FN_appsをcheckoutする。
```bash
cd benchpark
git checkout FN_apps 
```
### 2.3 venvを作成する。
　venvはアーキ依存がある。X86で作成したvenvはaarch64では利用できない。\
　複数の異なるアーキで利用する場合は、アーキ毎に作成し、使い分ける。\
　下記の事例は、x86用とaarch64用のvenvを作成する例です。必要に応じて、各マシンにログインしてからvenvを作成する。\
　このvenvは、benchparkコマンドおよび、rambleコマンドの両方で必要になる。
* x86マシンにログイン
```bash
python -m venv .venv_x86
```
* aarch64マシンにログイン
```bash
python -m venv .venv_aarch64
```
### 2.4 venvのアクティベート
```bash
source .venv_x86/bin/activate
```
### 2.5 pipのセットアップ
　pipを最新化
```bash
pip install --upgrade pip
```
　benchparkの動作に必要なパッケージをインストール
```bash
pip install -r requirements.txt
```
```bash
pip install .[analyze]
```
### 2.6 benchpark用設定スクリプトを読み込む
```bash
source ./setup-env.sh
```
---
## 3. アプリの設定情報を登録する
アプリ毎に、以下の3種の設定ファイルを作成する。\
何を記載すべきか分からない場合は、[マニュアル](https://software.llnl.gov/benchpark/add-a-benchmark.html)または登録済みアプリの設定ファイルを参照して作成する。
### 3.1 package.py
spack用の設定を package.py に記述し、以下のパスに配置する。\
'[apps]' の部分は自身のアプリ名に変更する。
```bash
benchpark/repos/spack_repo/benchpark/packages/[apps]/package.py
```
### 3.2 application.py
アプリの実行方法を application.py に記述し、以下のパスに配置する。（入力データ、実行パターン、figure_of_merit など）\
'[apps]' の部分は自身のアプリ名に変更する。
```bash
benchpark/repos/ramble_applications/[apps]/application.py
```
FOM(figure_of_merit) の設定は、application.py に記載する。\
ここで記載した内容が、ramble analyze で出力される。
### 3.3 experiment.py
アプリを実行する際の条件を experiment.py に記述し、以下のパスに配置する。（並列数やアプリ実行時のパラメータなど）\
'[apps]' の部分は自身のアプリ名に変更する。[マニュアル](https://software.llnl.gov/benchpark/add-an-experiment.html)
```bash
benchpark/experiments/[apps]/experiment.py
```
---
## 4. benchparkコマンドの実行
以降は、アプリの環境構築から実行および分析までの手順について、saxpyを事例として記載する。
'saxpy'の部分を自身のアプリ名に変えることで、再利用できる。
### 4.1 system init
* gh200上で、gccでコンパイルする場合の事例 \
'dest' に、設定を格納するディレクトリ名を指定する（ディレクトリ名は任意）\
'riken-cloud' は、system.py を格納しているディレクトリ名（富岳の場合は、riken-fugaku になる）\
'cluster' に、機種名(gh200)を指定する。（使用する機種に応じてクラスタ名を変更する）\
'compiler' に、使用するコンパイラを指定する。（gcc, cuda, nvhpc などが指定できる）
```bash
benchpark system init --dest=gh200 riken-cloud cluster=gh200 compiler=gcc
```
### 4.2 experiment init
* saxpyを対象にinitする事例 \
下記の 'gh200' は、4.1 のdestで作成したディレクトリ名。'saxpy' は、アプリ名。
```bash
benchpark experiment init gh200 saxpy
```
### 4.3 setup
* saxpyを対象にsetupする事例 \
下記の 'gh200/saxpy' は、[4.1のdestで作成したディレクトリ名] / [4.2のアプリ名] \
'workspace' は、作成するワークスペースの名前（名前は任意）
```bash
benchpark setup gh200/saxpy workspace
```
---
## 5. rambleコマンドの実行
### 5.1 評価対象マシンにログインする
rccs-cloud で gh200 を使用する場合の事例
```bash
srun -N 1 -p qc-gh200 --time=02:00:00 --pty bash
```
### 5.2 venvの確認
以下で、パスが表示されることを確認する。
もし、何も表示されない場合は、2.4 および 2.6 を実行する。
```bash
echo $VIRTUAL_ENV
```
### 5.3 ramble用設定スクリプトを読み込む
```bash
source ./workspace/setup.sh
```
### 5.4 setup
spackを使用してビルドするフェーズ。以下を実行すると、内部で 'spack install' が発行される。
```bash
ramble --workspace-dir ./workspace/gh200/saxpy/workspace workspace setup
```
### 5.5 on
ジョブを起動する。slurmであれば、自動的にsbatchでジョブ投入される。
```bash
ramble --workspace-dir ./workspace/gh200/saxpy/workspace on
```
### 5.6 analyze
実行結果からFOMを抽出できる。
```bash
ramble --workspace-dir ./workspace/gh200/saxpy/workspace workspace analyze
```
---
[GH200でsaxpyをセットアップする事例](Case_Studies/GH200/GH200_saxpy_gcc_JP.md) \
[Genoaでsaxpyをセットアップする事例](Case_Studies/GENOA/GENOA_saxpy_gcc_JP.md) \
[DGXでsaxpyをセットアップする事例](Case_Studies/DGX/DGX_saxpy_gcc_JP.md) \
[FX700でsaxpyをセットアップする事例](Case_Studies/FX700/FX700_saxpy_fj_JP.md) \
[富岳でsaxpyをセットアップする事例](Case_Studies/FUGAKU/FUGAKU_saxpy_fj_JP.md)
