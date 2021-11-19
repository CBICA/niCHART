# This Python file uses the following encoding: utf-8
"""
contact: software@cbica.upenn.edu
Copyright (c) 2018 University of Pennsylvania. All rights reserved.
Use of this source code is governed by license located in license file: https://github.com/CBICA/BrainChart/blob/main/LICENSE
"""
from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib as mpl
mpl.use('QT5Agg')


class PlotCanvas(FigureCanvas):
    """ A generic Plotting class that derives from FigureCanvasQTAgg
    and plots data as per different options"""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        """The constructor."""

        # a figure instance to plot on
        self.fig = mpl.figure.Figure(figsize=(width, height), dpi=dpi)

        #super clas
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

