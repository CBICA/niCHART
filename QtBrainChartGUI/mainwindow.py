# This Python file uses the following encoding: utf-8
"""
contact: software@cbica.upenn.edu
Copyright (c) 2018 University of Pennsylvania. All rights reserved.
Use of this source code is governed by license located in license file: https://github.com/CBICA/BrainChart/blob/main/LICENSE
"""

from PyQt5 import QtCore, QtWidgets, uic
from yapsy.PluginManager import PluginManager
from yapsy.IPlugin import IPlugin
import os, sys
#from BrainChart.dataio import DataIO
from QtBrainChartGUI.core.model.datamodel import DataModel

import pandas as pd

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, dataFile=None, harmonizationModelFile=None, SPAREModelFile=None):
        super(MainWindow,self).__init__()
        self.SetupUi()
        self.SetupConnections()
        #defaults
        print("in constructor")

        #instantiate data model
        self.datamodel = DataModel()

        # Create plugin manager
        self.manager = PluginManager(categories_filter={ "UI": IPlugin})
        root = os.path.dirname(__file__)
        self.manager.setPluginPlaces([os.path.join(root, 'plugins')])
        #self.manager.setPluginPlaces(["plugins"])

        # Load plugins
        self.manager.locatePlugins()
        p = self.manager.loadPlugins()

        self.Plugins = {}
        for plugin in self.manager.getPluginsOfCategory("UI"):
            # plugin.plugin_object is an instance of the plugin
            po = plugin.plugin_object
            po.datamodel = self.datamodel
            po.SetupConnections()
            self.Plugins[plugin.name] = po
            print("plugins: ", plugin.name)
            #self.ui.tabWidget.addTab(po.getUI(),plugin.name)
            self.ui.tabWidget.addTab(po,plugin.name)

        if dataFile is not None:
            # if datafile provided on cmd line, load it
            self.OnDataFile(dataFile)


        if harmonizationModelFile is not None:
            pass
            #if harmonization model file provided on cmd line, load it
            #self.OnHarmonizationModelFileOpenClicked(harmonizationModelFile)
        if SPAREModelFile is not None:
            pass
            #if SPARE model file provided on cmd line, load it
            #self.OnSPAREModelFileOpenClicked(SPAREModelFile)

    def SetupConnections(self):
        self.actionAbout.triggered.connect(self.OnAboutClicked)
 
    def SetupUi(self):
        print("in setup")
        root = os.path.dirname(__file__)
        self.ui = uic.loadUi(os.path.join(root, 'mainwindow.ui'), self)
        self.ui.setWindowTitle('Neuro-imaging brain aging chart')

    def OnAboutClicked(self):
        #quit application
        #QtWidgets.QApplication.quit()
        print("About Clicked")

    def OnCloseClicked(self):
        #close currently loaded data and model
        QtWidgets.QApplication.quit()


    def OnDataFile(self, dataFile):
        self.datamodel.SetDataFilePath(dataFile)
        self.datamodel.SetData(pd.read_pickle(dataFile))


    def ResetUI(self):
        #reset all UI
        pass
