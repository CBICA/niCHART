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

The easiest method to install the toolbox is via the binary installers for Windows, macOS, and Linux.

Alternate releases of **[NiBAχ]** can be found `here <https://github.com/CBICA/NiBAx/tags>`_. 


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
Supported input formats are ``*.csv`` and ``*.pkl/*.pkl.gz``.

AgeTrends
=========
This plugin will show MUSE and WMLS volumes as a function of age.
The data points are colored by category in categorical variables found in the
data set.
In the top left drop-down menu, the region of interest can be selected.
The text field of the menu can be used to search for variable names.
If a suitable ``neuroHarmonize`` model is loaded (plugin ``Harmonization``),
the harmonized muse volumes (i.e. ``H_MUSE_Volume_*``) will also show the
age-conditional normative range for an average intracranial volume.

.. figure:: images/ScreenshotAgeTrend.png


MUSE Harmonization
==================
This plugin will show the distribution of the residuals of raw and harmonized MUSE volumes, 
as well as the harmonization parameters ('Location' and 'Scale') associated with each ``SITE``.
The boxplots are colored by the ``SITE`` variable found in the
data set.
After loading the model, the plugin will verify that the loaded model is
compatible.
In the top left drop-down menu, the region of interest can be selected.
The text field of the menu can be used to search for variable names.
The plugin will provide harmonized MUSE volumes, which can be added to the input data 
for analysis in the ``AgeTrends`` plugin. It will also add the residuals
calculated in the harmonization process for use in SPARE-* score calculation in
the ``SPARE-*`` plug in.

.. figure:: images/ScreenshotHarmonization.png


SPARE-*
=======
This plugin is used to load a SPARE-* model, apply it ot the data set, and
optionally add the derived scores to the data set.
Currently only ``SPARE-AD`` and ``SPARE-BA`` are supported.
After loading the model, the plugin will verify that the loaded model is
compatible.
To be applied to the data, harmonized features need to be present in the data
frame.
After running the plugin ``Harmonization``, the necessary standardized features
are available.
The computation of the scores runs asyncronously, which means that the rest of
the user interface remains operational.

.. figure:: images/ScreenshotSPARE.png
