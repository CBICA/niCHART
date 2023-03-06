# [niCHART] The neuro-imaging brain aging chart

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/7aadb18130574bd5b85b978cd709fe2c)](https://www.codacy.com/gh/CBICA/NiBAx/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=CBICA/NiBAx&amp;utm_campaign=Badge_Grade)

| :construction:
  <font size="+1">This software and documentation is under development!
                  Check out up-to-date documentation at
                  [cbica.github.io/niCHART/](https://cbica.github.io/niCHART/) </font> :construction: |
|-----------------------------------------|

The neuro-imaging brain aging chart **[niCHART]** is a comprehensive solution to
analyze standard structural and functional brain MRI data across studies.
**[niCHART]** and the associated pre-processing tools implement computational
morphometry, functional signal analysis, quality control, statistical
harmonization, data standardization, interactive visualization, and extraction
of expressive imaging signatures.

This `README` is intended for contributors and developers.
User documentation is available at
[cbica.github.io/niCHART/](https://cbica.github.io/niCHART/).


<figure>
  <img src="niCHART/resources/workflow.gif" alt="[niCHART] Demo"/>
  <figcaption>Demonstration of the [niCHART] graphical user interface.</figcaption>
</figure>


## Setup for development
Install Python version 3.8.8 or newer.
The exact procedure depends on the operating system and configuration.
Verify the version with

```shell
python --version # should be 3.8.8 or newer
```


### Prepare conda environment
Assuming current working directory is `niCHART` and containing the source code
cloned from https://github.com/CBICA/niCHART.git.

Ensure Anaconda is installed. Follow instructions for user's operating system [here](https://docs.anaconda.com/anaconda/install/index.html). After Anaconda has been installed, be sure to exit and reopen any 
command line windows to use `conda` command


```shell
conda create -n niCHART python=3.8.8  
conda activate niCHART
python -m pip install --upgrade pip
```


### Prepare environment in Linux (CUBIC)
Assuming current working directory is `niCHART` and containing the source code
cloned from https://github.com/CBICA/niCHART.git.

```shell
python -m venv .env
.env/bin/activate
python -m pip install --upgrade pip
```

### Prepare environment for PowerShell (Windows 10 or 11)
Assuming current working directory is `niCHART` and containing the source code
cloned from https://github.com/CBICA/niCHART.git.

```shell
python -m venv .env
& .env/Scripts/Activate.ps1
python -m pip install --upgrade pip
```


### Install the [niCHART] software
To install the [niCHART], install it in a virtual or conda environment.
Depending on the desired version, use one of the following
commands to install it.

```shell
# Editable version for development after cloning https://github.com/CBICA/niCHART.git 
python -m pip install -U -e .
poetry install

# Version from pull request (#57 in this example) for testing proposed changes
python -m pip install -U git+https://github.com/CBICA/niCHART.git@refs/pull/57/head

# Main version of toolbox
python -m pip install -U git+https://github.com/CBICA/niCHART.git
```


## Usage
After proper installation, the standalone graphical user interface can be launched
in the terminal with:

```shell
niCHART
```

The data file can be passed as command line argument `--data_file` as shown below.

```shell
niCHART --data_file istaging.pkl.gz
```

## Build executable package for Windows 10/11
We use (beeware/briefcase)[https://github.com/beeware/briefcase)] to package
the software in Windows 10/11.

```shell
briefcase create 
briefcase update
briefcase package
```

The result is an installer `niCHART.msi` that will install the app in the
user's profile. The installation does not require administrator rights.

## Disclaimer
- The software has been designed for research purposes only and has neither been reviewed nor approved for clinical use by the Food and Drug Administration (FDA) or by any other federal/state agency.
- By using NiBAx, the user agrees to the following license: https://www.med.upenn.edu/cbica/software-agreement-non-commercial.html

## Contact
For more information and support, please post on the [Discussions](https://github.com/CBICA/niCHART/discussions) section or contact <a href="mailto:software@cbica.upenn.edu">CBICA Software</a>.
