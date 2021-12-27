# [NiBAx] The neuro-imaging brain aging chart

**This software is under development!**

![](NiBAx/resources/workflow.gif)


## Setup for development
Install Python version 3.8.8 or newer.
The exact procedure depends on the operating system and configuration.
Verify the version with

```shell
python --version # should be 3.8.8 or newer
```

### Prepare environment in Linux (CUBIC)
Assuming current working directory is `NiBAx` and containing the source code
cloned from https://github.com/CBICA/NiBAx.git.

```shell
python -m venv .env
.env/bin/activate
python -m pip install --upgrade pip
```

### Prepare environment in Windows 10 or Windows 11
Assuming current working directory is `NiBAx` and containing the source code
cloned from https://github.com/CBICA/NiBAx.git.

```shell
python -m venv .env
& .env/Scripts/Activate.ps1
python -m pip install --upgrade pip
```

### Install [NiBAx] Toolbox
To install the [NiBAx], install it in a virtual environment. Depending on the
desired version, use one of the following commands to install it.

```shell
# Editable version for development after cloning https://github.com/CBICA/NiBAx.git 
python -m pip install -U -e . 

# Version from pull request (#57 in this example) for testing proposed changes
python -m pip install -U git+https://github.com/CBICA/NiBAx.git@refs/pull/57/head

# Main version of toolbox
python -m pip install -U git+https://github.com/CBICA/NiBAx.git
```


## Useage
After proper installation, the standalone graphical user interface can be launched
in the terminal with:

```shell
NiBAx
```

The data file can be passed as command line argument `--data_file` as shown below.

```shell
NiBAx --data_file istaging.pkl.gz
```
