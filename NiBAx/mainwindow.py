# This Python file uses the following encoding: utf-8
"""
contact: software@cbica.upenn.edu
Copyright (c) 2018 University of Pennsylvania. All rights reserved.
Use of this source code is governed by license located in license file: https://github.com/CBICA/BrainChart/blob/main/LICENSE
"""

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from yapsy.PluginManager import PluginManager
from yapsy.IPlugin import IPlugin
import os, sys
#from BrainChart.dataio import DataIO
from NiBAx.core.model.datamodel import DataModel
from .aboutdialog import AboutDialog
from NiBAx.resources import resources
from PyQt5.QtWidgets import QAction
import pandas as pd
from NiBAx.core.baseplugin import BasePlugin
from NiBAx.core import iStagingLogger

logger = iStagingLogger.get_logger(__name__)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, dataFile=None, harmonizationModelFile=None, SPAREModelFile=None):
        super(MainWindow,self).__init__()

        #log
        logger.info('New NiBAx session starting...')

        self.SetupUi()
        self.SetupConnections()

        #instantiate data model
        self.datamodel = DataModel()

        # Create plugin manager
        self.manager = PluginManager(categories_filter={ "Tabs": BasePlugin})
        root = os.path.dirname(__file__)
        self.manager.setPluginPlaces([os.path.join(root, 'plugins')])

        # Load plugins
        self.manager.locatePlugins()
        self.manager.loadPlugins()

        #create dictionary of plugins with key = plugin name, value = plugin instance
        self.Plugins = {}
        for plugin in self.manager.getAllPlugins():
            # plugin.plugin_object is an instance of the plugin
            po = plugin.plugin_object
            po.datamodel = self.datamodel
            po.SetupConnections()
            self.Plugins[plugin.name] = po

        logger.info("Loaded Plugins: %s", self.Plugins.keys())

        #organize plugins in order:Data -> Characteristics -> Age Trends -> Harmonization -> SPARE-*
        for num in range(len(self.Plugins)):
            for key,value in self.Plugins.items():
                if(num == value.getTabPosition()):
                    self.ui.tabWidget.insertTab(value.getTabPosition(),value,key)
                    break

        self.ui.tabWidget.setCurrentIndex(0) # always display first tab

        if dataFile is not None:
            # if datafile provided on cmd line, load it
            self.Plugins['Data'].ReadData(dataFile)

        if harmonizationModelFile is not None:
            pass
            #if harmonization model file provided on cmd line, load it
            #self.OnHarmonizationModelFileOpenClicked(harmonizationModelFile)
        if SPAREModelFile is not None:
            pass
            #if SPARE model file provided on cmd line, load it
            #self.OnSPAREModelFileOpenClicked(SPAREModelFile)
        
        # Include Mac menu bar
        self.ui.actionHelp.setMenuRole(QAction.NoRole)
        self.ui.actionAbout.setMenuRole(QAction.NoRole)

    def __del__(self):
        logger.info('NiBAx session ending...')

    def SetupConnections(self):
        self.actionAbout.triggered.connect(self.OnAboutClicked)
        self.actionHelp.triggered.connect(self.OnHelpClicked)
 
    def SetupUi(self):
        root = os.path.dirname(__file__)
        self.ui = uic.loadUi(os.path.join(root, 'mainwindow.ui'), self)
        self.ui.setWindowTitle('NiBAx')
        self.setWindowIcon(QtGui.QIcon(":/images/NiBAX Logo.png"))
        self.aboutdialog = AboutDialog(self)

    def OnAboutClicked(self):
        self.aboutdialog.show()

    def OnHelpClicked(self):
        url = QtCore.QUrl('https://github.com/CBICA/iSTAGING-Tools')
        QtGui.QDesktopServices.openUrl(url)

    def OnCloseClicked(self):
        #close currently loaded data and model
        QtWidgets.QApplication.quit()

    def ResetUI(self):
        #reset all UI
        pass
