import wx
import pandas as pd

import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import (
    FigureCanvasWxAgg as FigureCanvas,
    NavigationToolbar2WxAgg as NavigationToolbar)

from pubsub import pub
from pyguitemp.plugins import PluginBase, Tab
from typing import Callable, Optional


class NotebookPlugin(PluginBase):
    def tabs(self, parent):
        age_trends = Tab(
            page=BasicPlot(parent),
            text="MUSE age trends",
        )
        pub.subscribe(self.plot, "data.load")

        return [age_trends]


    def plot(self, filename: str, data: Optional[pd.DataFrame] = None):
        print("BlaBla")


class BasicPlot(wx.Panel):

    def __init__(self, parent) -> None:
        super(BasicPlot, self).__init__(parent, style=wx.TE_MULTILINE | wx.TE_READONLY)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.label = wx.StaticText(self, label="MUSE age trends" )
        ROIs = ['MUSE_Volume_702', 'MUSE_Volume_47']
        hues = ['Sex', 'Study', 'SITE']
        self.comboROI = wx.ComboBox(self, choices=ROIs, value='MUSE_Volume_47')
        self.comboHue = wx.ComboBox(self, choices=hues, value='Study')
        self.Bind(wx.EVT_COMBOBOX, self.onCombo)
        hbox.Add(self.label, flag=wx.EXPAND | wx.ALL, border=10)
        hbox.Add(self.comboROI, flag=wx.EXPAND | wx.ALL, border=10)
        hbox.Add(self.comboHue, flag=wx.EXPAND | wx.ALL, border=10)

        self.data = None
        pub.subscribe(self.set_data, "data.load")
        self.figure = mpl.figure.Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.Realize()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(hbox)
        sizer.Add(self.canvas, 1, wx.EXPAND)
        sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        self.SetSizer(sizer)
        #self.Fit()
        self.plot()


    def set_data(self, filename: str, data: Optional[pd.DataFrame] = None):
        self.data = data
        self.plot()
    

    def onCombo(self, event):
        self.plot()

    def plot(self):
        if self.data is not None:
            self.axes.clear()
            sns.scatterplot(x='Age', y=self.comboROI.GetValue(), data=self.data, 
                            hue=self.comboHue.GetValue(), ax=self.axes)
            self.axes.legend(bbox_to_anchor=(1.01, 1), borderaxespad=0)
            self.figure.tight_layout()
            plt.draw()
        else:
            self.axes.clear()
            self.axes.text(0.5, 0.5, 'No data loaded.')

        self.canvas.draw()