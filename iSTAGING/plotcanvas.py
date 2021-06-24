# This Python file uses the following encoding: utf-8
"""
contact: software@cbica.upenn.edu
Copyright (c) 2018 University of Pennsylvania. All rights reserved.
Use of this source code is governed by license located in license file: https://github.com/CBICA/iSTAGING-Tools/blob/main/LICENSE
"""
from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import seaborn as sns
import random

class PlotCanvas(FigureCanvas):
    """ A generic Plotting class that derives from FigureCanvasQTAgg
    and plots data as per different options"""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        """The constructor."""

        # a figure instance to plot on
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        #super clas
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def Plot(self,datamodel,plotOptions):
        """call appropriate plotting functionality as per plot options"""
        if(str(plotOptions['VIEW']) == 'AgeTrend'):
            self.PlotAgeTrends(datamodel,plotOptions)
        elif(str(plotOptions['VIEW']) == 'View2'):
            self.PlotView2(datamodel,plotOptions)

    def PlotAgeTrends(self,datamodel,plotOptions):
        """Plot Age Trends - default view"""

        currentROI = plotOptions['ROI']
        currentHue = plotOptions['HUE']

        if not currentHue:
            currentHue = 'Sex'

        # clear plot
        self.axes.clear()

        # seaborn plot on axis
        sns.scatterplot(x='Age', y=currentROI,  hue=currentHue,ax=self.axes, s=5,
                       data=datamodel.GetData(currentROI,currentHue))

        # Plot normative range if according GAM model is available
        if (datamodel.harmonization_model is not None) and (currentROI in datamodel.harmonization_model['ROIs']):
            x,y,z = datamodel.GetNormativeRange(currentROI)
            print('Pooled variance: %f' % (z))
            # Plot three lines as expected mean and +/- 2 times standard deviation
            sns.lineplot(x=x, y=y, ax=self.axes, linestyle='-', markers=False, color='k')
            sns.lineplot(x=x, y=y+z, ax=self.axes, linestyle=':', markers=False, color='k')
            sns.lineplot(x=x, y=y-z, ax=self.axes, linestyle=':', markers=False, color='k')

        # refresh canvas
        self.draw()

    def PlotView2(self,datamodel,plotOptions):
        """Plot View 2"""

        # clear plot
        self.axes.clear()

        #plot other/modified data
        otherdata = [random.random() for i in range(25)]
        self.axes.plot(otherdata, 'r-')
        self.axes.set_title('PyQt Matplotlib Example')

        # refresh canvas
        self.draw()
