##########
User Guide
##########

.. warning::
   The documentation and GUI is under active development.
   Statistical and machine learning models will be made available once fully
   validated.


************
Installation
************

Until one-click installation packages are available, we recommend to install
an up-to-date version of **[NiBAχ]** using `pip`.
The only requirement is Python 3.8 or newer.
All dependencies will be installed automatically.
The software is compatible with Windows 10/11, macOS, and Linux.

To start the installation, start a terminal and check the installed version
of Python.
The output should show a version `3.8` or newer.
If the command is not recognized, Python is not installed or the `python` command
is not found by the system.
If Python is installed--for instance in Windows, it is possible to call the command
with the full path.

.. tabs::

   .. code-tab:: text Windows 10/11

         python --version
         # or, if `python` not in PATH
         C:\Users\USERNAME\AppData\Local\Programs\Python\Python39\python.exe --version

   .. code-tab:: shell macOS

         /usr/bin/python --version

   .. code-tab:: shell Linux

         /usr/bin/python --version


It is recommended to install **[NiBAx]** in a virtual Python environment.
Shown below is an installation into the folder `.env` in the current working
directory.

.. code-block:: shell

    python -m venv .env
    source .env/bin/activate
    python -m pip install https://github.com/CBICA/NiBAx


Once installed, the GUI is accesible as command `NiBAx`.

.. code-block:: shell

    # Typing NiBAx in an activated virtual environment
    # will launch the graphical user interface.
    NiBAx


*********
Quickstart
*********

To quickly set up and use the GUI, download the following test files: 

:download:`Example dataset  <synthetic_MUSE_ROI_dataset.pkl.gz>`

:download:`Example model for MUSE harmonization  <synthetic_MUSE_harmonization_model.pkl>`

After following the previous section, starting the GUI requires activation of
the virtual Python environment in every terminal window in which the application
is to be launched. Typically, as follows:

.. tabs::

   .. code-tab:: text PowerShell (Windows 10/11)

    & .env/Scripts/Activate.ps1
    NiBAx.exe

   .. code-tab:: shell Bash (Linux and macOS)

    source /path/to/.env/bin/activate
    NiBAx


This will launch the GUI.

.. figure:: workflow.gif

************
Core Plugins
************

**The documentation is under active development.**

The following core plugins are bundled with the application.

I/O
===
The input and output (I/O) plugin is concerned with loading and saving data
tables.

MUSE Harmonization
==================
TODO: Add screenshot and description

.. figure:: images/ScreenshotHarmonization.png

MUSE QC
=======
TODO: Add screenshot and description

SPARE-*
=======
TODO: Add screenshot and description

.. figure:: images/ScreenshotSPARE.png

AgeTrends
=========
TODO: Add screenshot and description

.. figure:: images/ScreenshotAgeTrend.png
