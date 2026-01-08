# Running benchpark on Fugaku; `saxpy%fj`

## Repository Preparation

To avoid i-node exhaustion, work in a data area rather than under the home directory.

```bash
cd <not under $HOME>
```

For safety, also ensure that you are working in a path that does **not** contain symbolic links  
(because paths including symbolic links have caused workspace path issues in the past).

```bash
cd $(pwd -P)
git clone https://github.com/RIKEN-RCCS/benchpark
cd benchpark
```

## Python Environment Setup

Perform the following steps on a **compute node**.

```bash
pjsub --interact -L "node=1" -L "rscgrp=int" -L "elapse=5:55:00" --sparam "wait-time=600" --all-mount-gfscache
```

```bash
. /vol0004/apps/oss/spack/share/spack/setup-env.sh
spack load --sh --first python@3.8: arch=linux-rhel8-a64fx > load-python-cn.sh
. ./load-python-cn.sh
python3 -m venv my-env-cn
. ./my-env-cn/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Environment Variable Configuration

```bash
. ./setup-env.sh
export SYS="riken-fugaku"
export WSDIR="$(pwd)/workspace"
```

## Change the Location of the `bootstrap` Directory

```bash
benchpark configure --bootstrap-location ./bootstrap
benchpark bootstrap
benchpark info system $SYS  # verify
```

(This step takes time because it clones `ramble/spack-packages/spack`.)

## Workspace Creation

```bash
benchpark system init --dest=fugaku_fj ${SYS} compiler=fj
benchpark experiment init fugaku_fj saxpy
benchpark setup fugaku_fj/saxpy ${WSDIR}
```

(This step also takes time because it clones `ramble/spack-packages/spack`.)

## Recipe Modifications, etc.

### `fujitsu-mpi`

```bash
cp /vol0004/apps/oss/spack-v1.0.1/var/spack/fugaku-packages/repos/spack_repo/fugaku/local/packages/fujitsu_mpi/package.py \
   ./workspace/spack-packages/repos/spack_repo/builtin/packages/fujitsu_mpi/package.py
```

## Build an Experiment

```bash
. ${WSDIR}/setup.sh
cd workspace/fugaku_fj/saxpy/workspace/
ramble --workspace-dir . workspace setup
```

At this stage, `spack install` is executed.

## Run the Experiment

Run and analyze the benchmark from the **login node**.

### Exit the Compute Node

```bash
exit
```

### Python Environment Setup on the Login Node

```bash
. /vol0004/apps/oss/spack/share/spack/setup-env.sh
spack load --sh --first python@3.8: arch=linux-rhel8-cascadelake > load-python-ln.sh
. ./load-python-ln.sh
pip install --upgrade pip
pip install -r requirements.txt
pip install .[analyze]
```

### Submit the Benchmark Job

```bash
. ./setup-env.sh
. ./workspace/setup.sh
ramble --workspace-dir ./workspace/fugaku_fj/saxpy/workspace on
```

### Check Results

```bash
find workspace/fugaku_fj/saxpy/workspace/experiments/saxpy/ -type f
```

### Analysis

```bash
ramble --workspace-dir ./workspace/fugaku_fj/saxpy/workspace workspace analyze
```
