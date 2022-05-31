###############
Developer Guide
###############

.. warning::
   The documentation and GUI is under active development.
   Statistical and machine learning models will be made available once fully
   validated.


***************************
Build documentation locally
***************************

When ``sphinx-autobuild`` is installed, the documentation can bu built locally
and automatically updates when one of the source files changes.

.. code-block:: shell

   sphinx-autobuild.exe docs docs/_build/html


The tabbed code blocks require the package ``sphinx-tabs``.
PDF build requires ``rst2pdf``.
``myst_parser``, ``sphinx_rtd_theme``, ``sphinx_gallery``, and
``sphinx-autoapi[extension]``.
