---

## 1. Verify the Python environment

Python version 3.10 or later is required. Check the installed Python version using the command below. If the version is earlier than 3.10, install a newer version of Python.
```bash
python --version
```
---

## 2. Set up Benchpark
### 2.1 Clone the environment from GitHub
```bash
git clone https://github.com/RIKEN-RCCS/benchpark
```
### 2.2 Check out FN_apps
```bash
cd benchpark
git checkout FN_apps 
```
### 2.3 Create venv
  The venv is architecture-dependent. A venv created on x86 cannot be used on aarch64. \
  If the environment will be used on multiple architectures, create a separate venv for each architecture and use them accordingly. \
  The following example demonstrates how to create venv environments for x86 and aarch64. \
  Log in to each machine as necessary before creating the corresponding venv. \
  This venv is required for both the benchpark command and the ramble command.
* Log in to the x86 machine
```bash
python -m venv .venv_x86
```
* Log in to the aarch64 machine
```bash
python -m venv .venv_aarch64
```
### 2.4 Activate venv
```bash
source .venv_x86/bin/activate
```
### 2.5 Set up pip
　Upgrade pip to the latest version
```bash
pip install --upgrade pip
```
　Install the packages required for Benchpark operation
```bash
pip install -r requirements.txt
```
```bash
pip install .[analyze]
```
### 2.6 Load the configuration script for Benchpark
```bash
source ./setup-env.sh
```
---
## 3. Register the application configuration information
Register the application configuration information. \
If you are unsure what to include, refer to the [documentation](https://software.llnl.gov/benchpark/add-a-benchmark.html) or other registered applications.
### 3.1 package.py
Write the Spack configuration in 'package.py' and place it in the following path. \
Replace '[apps]' with your application name.
```bash
benchpark/repos/spack_repo/benchpark/packages/[apps]/package.py
```
### 3.2 application.py
Describe how to run the application in 'application.py' and place it in the following path (including input data, execution patterns, figure of merit, etc.).\
Replace '[apps]' with your application name.
```bash
benchpark/repos/ramble_applications/[apps]/application.py
```
The FOM (figure_of_merit) configuration should also be defined in application.py. \
The content specified here will be used as the output of 'ramble analyze'.
### 3.3 experiment.py
Define the execution conditions for the application in 'experiment.py' and place it in the following path (such as number of parallel processes and runtime parameters).\
Replace '[apps]' with your application name. [documentation](https://software.llnl.gov/benchpark/add-an-experiment.html)
```bash
benchpark/experiments/[apps]/experiment.py
```
---
## 4. Run the benchpark command
The following sections describe the steps from environment setup to execution and analysis of the application, using saxpy as an example. \
By replacing saxpy with your own application name, this procedure can be reused.
### 4.1 system init
* Example for compiling with GCC on GH200 \
Specify in 'dest' the directory name where the settings will be stored (the directory name can be arbitrary). \
'riken-gh200' refers to the directory containing system.py (for Fugaku, this becomes riken-fugaku). \
In 'compiler', specify the compiler to be used (e.g., gcc, cuda, nvhpc, etc.).
```bash
benchpark system init --dest=gh200 riken-gh200 compiler=gcc
```
### 4.2 experiment init
* Example of 'init' for the SAXPY case \
In the following example, 'gh200' refers to the directory created as 'dest' in section 4.1. \
'saxpy' is the application name.
```bash
benchpark experiment init gh200 saxpy
```
### 4.3 setup
* Example of 'setup' for the SAXPY case \
In the following example, 'gh200/saxpy' refers to [directory name created as dest in 4.1] / [application name in 4.2]. \
'workspace' is the name of the workspace to be created (the name can be arbitrary).
```bash
benchpark setup gh200/saxpy workspace
```
---
## 5. Run the ramble command
### 5.1 Log in to the target evaluation machine
Example for using GH200 on rccs-cloud.
```bash
srun -N 1 -p qc-gh200 --time=02:00:00 --pty bash
```
### 5.2 Check the 'venv'
Verify that the path is displayed using the command below.
If nothing is displayed, run steps 2.4 and 2.6.
```bash
echo $VIRTUAL_ENV
```
### 5.3 Load the configuration script for ramble
```bash
source ./workspace/setup.sh
```
### 5.4 setup
Phase for building using Spack. Running the following will internally execute 'spack install'.
```bash
ramble --workspace-dir ./workspace/gh200/saxpy/workspace workspace setup
```
### 5.5 on
Launch the job. If using Slurm, the job will be automatically submitted via sbatch.
```bash
ramble --workspace-dir ./workspace/gh200/saxpy/workspace on
```
### 5.6 analyze
The FOM can be extracted from the execution results.
```bash
ramble --workspace-dir ./workspace/gh200/saxpy/workspace workspace analyze
```
---
[利用手引き(日本語版)](User_Guide_JP.md) \
[Example of setting up SAXPY on GH200](Case_Studies/GH200/GH200_saxpy_gcc.md) [&nbsp;&nbsp;(日本語)&nbsp;](Case_Studies/GH200/GH200_saxpy_gcc_JP.md)\
[Example of setting up SAXPY on Genoa](Case_Studies/GENOA/GENOA_saxpy_gcc.md) [&nbsp;&nbsp;(日本語)&nbsp;](Case_Studies/GENOA/GENOA_saxpy_gcc_JP.md)\
[Example of setting up SAXPY on DGX](Case_Studies/DGX/DGX_saxpy_gcc.md) [&nbsp;&nbsp;(日本語)&nbsp;](Case_Studies/DGX/DGX_saxpy_gcc_JP.md)\
[Example of setting up SAXPY on FX700](Case_Studies/FX700/FX700_saxpy_fj.md) [&nbsp;&nbsp;(日本語)&nbsp;](Case_Studies/FX700/FX700_saxpy_fj_JP.md)\
[Example of setting up SAXPY on Fugaku](Case_Studies/FUGAKU/FUGAKU_saxpy_fj.md) [&nbsp;&nbsp;(日本語)&nbsp;](Case_Studies/FUGAKU/FUGAKU_saxpy_fj_JP.md)
