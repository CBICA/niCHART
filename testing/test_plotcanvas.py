import pytest
import os
from PyQt5 import QtCore, QtWidgets
from niCHART.core.plotcanvas import PlotCanvas
import matplotlib

#This file contains tests for PlotCanvas.py

def test_init_PlotCanvas(qtbot):

    #instantiate PlotCanvas class to be tested
    plotCanvas = PlotCanvas()

    #read expected data
    fig = plotCanvas.getFigure()

    #compare read width and height of figure to default values from PlotCanvas constructor
    if (fig.get_figheight() == 4.0 and fig.get_figwidth() == 5.0):
        assert True
    else:
        assert False


