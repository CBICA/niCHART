#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Using the NiBAx API
===================

This example shows a simple ouse of the NiBAx API. The example is designed
to run inside the cloned `NiBAx` folder. It follows to some extent the
skelleton of `mainwindow.py` but without the GUI.
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

from PyQt5 import QtCore, QtWidgets

import NiBAx
from NiBAx.plugins.loadsave.dataio import DataIO
from NiBAx.core.plotcanvas import PlotCanvas



if __name__ == "__main__":

  # Load data
  root = os.path.dirname(__file__)
  dio = DataIO()
  df = dio.ReadPickleFile(os.path.join(root, '..', 'testing', 'Data', 'synthetic_data.pkl.gz'))
  print(df)
