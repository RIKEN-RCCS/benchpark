Example procedure for setting up and running SAXPY on the FUGAKU.
---
The complete workflow, from cloning benchpark to execution and analysis. \
After logging in to fugaku login node, execute the following commands. \
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
pjsub --interact -L "node=1" -L "rscgrp=int" -L "elapse=1:00:00" --sparam "wait-time=300" --all-mount-gfscache
python -m venv .venv_fugaku
source .venv_fugaku/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install .[analyze]
deactivate
exit
# The above 'venv' setup only needs to be performed once after running 'git clone'.
# Once the 'venv' has been created, the following steps can be repeated as needed.

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
# Wait until the job has completed.
ramble --workspace-dir ./workspace/fugaku/saxpy/workspace workspace analyze
```
---
__Additional Information__ \
The clone operation and `venv` setup only need to be performed once during the initial setup. \
After the `venv` has been created, the 'benchpark' and 'ramble' commands can be executed repeatedly. \
If the system used to create the `venv` differs from the system where it is executed, errors may occur. \
Therefore, when working within a single terminal session, switch the `venv` each time as appropriate. \
To avoid repeatedly switching `venv` environments, it is recommended to use separate terminals for login node and compute node.
