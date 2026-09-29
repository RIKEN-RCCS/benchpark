Example procedure for setting up and running SAXPY on the RIKYU environment of Riken.
---
The complete workflow, from cloning benchpark to execution and analysis. \
After logging in to login node on RIKYU, execute the following commands. \
Ensure that Python version 3.10 or later (`python@3.10+`) is available.
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
# The above 'venv' setup only needs to be performed once after running 'git clone'.
# Once the 'venv' has been created, the following steps can be repeated as needed.

source ./setup-env.sh
source ./workspace/setup.sh
benchpark system init --dest=rikyu riken-rikyu compiler=gcc
benchpark experiment init rikyu saxpy
benchpark setup rikyu/saxpy workspace
ramble --workspace-dir ./workspace/rikyu/saxpy/workspace workspace setup
ramble --workspace-dir ./workspace/rikyu/saxpy/workspace on
# Wait until the job has completed.
ramble --workspace-dir ./workspace/rikyu/saxpy/workspace workspace analyze
```
---
On the RIKYU environment, NVHPC is available for use.
(available versions: 26.5, 26.3, 25.11, 25.7, and 24.9)
```bash
benchpark system init --dest=rikyu riken-rikyu compiler=nvhpc  ← default is nvhpc@26.5
benchpark system init --dest=rikyu riken-rikyu compiler=nvhpc nvhpc=25.7  ← For switching to nvhpc@25.7
```
---
__Additional Information__ \
The clone operation and `venv` setup only need to be performed once during the initial setup. \
After the `venv` has been created, the 'benchpark' and 'ramble' commands can be executed repeatedly. 
