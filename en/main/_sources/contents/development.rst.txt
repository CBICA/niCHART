###############
Developer Guide
###############

.. warning::
   The documentation and GUI is under active development.
   Statistical and machine learning models will be made available once fully
   validated.

************
Installation
************

We recommend to install
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

***************************
Build documentation locally
***************************

When ``sphinx-autobuild`` is installed, the documentation can bu built locally
and automatically updates when one of the source files changes.

.. code-block:: shell

   sphinx-autobuild docs docs/_build/html


The tabbed code blocks require the package ``sphinx-tabs``.
PDF build requires ``rst2pdf``.
``myst_parser``, ``sphinx_rtd_theme``, ``sphinx_gallery``, and
``sphinx-autoapi[extension]``.
