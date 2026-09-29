Example procedure for setting up and running SAXPY on the DGX environment of RCCS-Cloud.
---
The complete workflow, from cloning benchpark to execution and analysis. \
After logging in to `login1` on RCCS-Cloud, execute the following commands. \
Ensure that Python version 3.10 or later (`python@3.10+`) is available.
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
# The above 'venv' setup only needs to be performed once after running 'git clone'.
# Once the 'venv' has been created, the following steps can be repeated as needed.

srun -N 1 -p ng-dgx-3h --time=06:00:00 --pty bash
source .venv_dgx/bin/activate
source ./setup-env.sh
source ./workspace/setup.sh
benchpark system init --dest=dgx riken-dgx compiler=gcc
benchpark experiment init dgx saxpy
benchpark setup dgx/saxpy workspace
ramble --workspace-dir ./workspace/dgx/saxpy/workspace workspace setup
deactivate
exit
source .venv_login/bin/activate
source ./setup-env.sh
source ./workspace/setup.sh
ramble --workspace-dir ./workspace/dgx/saxpy/workspace on
# Wait until the job has completed.
ramble --workspace-dir ./workspace/dgx/saxpy/workspace workspace analyze
```
---
On the DGX environment, NVHPC is available for use.
(available versions: 26.5 and 26.3)
```bash
benchpark system init --dest=dgx riken-dgx compiler=nvhpc  ← default is nvhpc@26.5
benchpark system init --dest=dgx riken-dgx compiler=nvhpc  nvhpc=26.3← default is nvhpc@26.3
```
---
__Additional Information__ \
The clone operation and `venv` setup only need to be performed once during the initial setup. \
After the `venv` has been created, the 'benchpark' and 'ramble' commands can be executed repeatedly. \
If the system used to create the `venv` differs from the system where it is executed, errors may occur. \
Therefore, when working within a single terminal session, switch the `venv` each time as appropriate. \
To avoid repeatedly switching `venv` environments, it is recommended to use separate terminals for 'login1' and 'gh200'.
