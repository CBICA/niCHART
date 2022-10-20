# This Python file uses the following encoding: utf-8
"""
contact: software@cbica.upenn.edu
Copyright (c) 2018 University of Pennsylvania. All rights reserved.
Use of this source code is governed by license located in license file: https://github.com/CBICA/NiBAx/blob/main/LICENSE
"""

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from yapsy.PluginManager import PluginManager
from yapsy.IPlugin import IPlugin
import os, sys
from NiBAx.core.dataio import DataIO
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
            
            print('PLUGIN ' + str(po))

        logger.info("Loaded Plugins: %s", self.Plugins.keys())

        #organize plugins in order:Data -> Characteristics -> Age Trends -> Harmonization -> SPARE-*
        for num in range(len(self.Plugins)):
            for key,value in self.Plugins.items():
                if(num == value.getTabPosition()):
                    print('Loading tab ' + str(num))
                    print(value)
                    self.ui.tabWidget.insertTab(value.getTabPosition(),value,key)
                    break

        self.ui.tabWidget.setCurrentIndex(0) # always display first tab

        if dataFile is not None:
            # if datafile provided on cmd line, load it
            #self.Plugins['Table View'].ReadData(dataFile)
            self.ReadData(dataFile)

        if harmonizationModelFile is not None:
            #if harmonization model file provided on cmd line, load it
            self.Plugins['Harmonization']. LoadHarmonizationModel(harmonizationModelFile)
        
        if SPAREModelFile is not None:
            pass
            #if SPARE model file provided on cmd line, load it
            #self.OnSPAREModelFileOpenClicked(SPAREModelFile)
        
        ## Include Mac menu bar
        #self.ui.menuFile.setMenuRole(QAction.NoRole)
        #self.ui.actionOpen.setMenuRole(QAction.NoRole)
        #self.ui.actionSave.setMenuRole(QAction.NoRole)

    def __del__(self):
        logger.info('NiBAx session ending...')

    def SetupConnections(self):
        self.actionOpen.triggered.connect(self.OnOpenClicked)
        self.actionSave.triggered.connect(self.OnSaveClicked)
        self.actionAbout.triggered.connect(self.OnAboutClicked)
 
    def SetupUi(self):
        root = os.path.dirname(__file__)
        self.ui = uic.loadUi(os.path.join(root, 'mainwindow.ui'), self)
        self.ui.setWindowTitle('NiBAx')
        self.setWindowIcon(QtGui.QIcon(":/images/NiBAX Logo.png"))
        self.aboutdialog = AboutDialog(self)

    #def _createMenuBar(self):
        #menuBar = self.menuBar()
        ## Creating menus using a QMenu object
        #fileMenu = QMenu("&File", self)
        #menuBar.addMenu(fileMenu)
        ## Creating menus using a title
        #editMenu = menuBar.addMenu("&Edit")
        #helpMenu = menuBar.addMenu("&Help")
        
    def ReadData(self,filename):
        #read input data
        dio = DataIO()
        if filename.endswith('.pkl.gz') | filename[0].endswith('.pkl'):
            d = dio.ReadPickleFile(filename)
        elif filename.endswith('.csv'):
            d = dio.ReadCSVFile(filename)
        else:
            d = None

        #also read MUSE dictionary
        MUSEDictNAMEtoID, MUSEDictIDtoNAME, MUSEDictDataFrame = dio.ReadMUSEDictionary()
        self.datamodel.SetMUSEDictionaries(MUSEDictNAMEtoID, MUSEDictIDtoNAME,MUSEDictDataFrame)

        #also read Derived MUSE dictionary 
        DerivedMUSEMap = dio.ReadDerivedMUSEMap()
        self.datamodel.SetDerivedMUSEMap(DerivedMUSEMap)

        #set data in model
        #if (d is not None) and self.datamodel.IsValidData(d):
        if (d is not None):
            logger.info('New data read from file: %s', filename)
            self.datamodel.SetDataFilePath(filename)
            self.datamodel.SetData(d)
        else:
            logger.warning('Loaded data was not valid.')
        
        
    def OnOpenClicked(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(None,
            caption = 'Open data file',
            directory = QtCore.QDir().homePath(),
            filter = "Pickle/CSV files (*.pkl.gz *.pkl *.csv)")

        if filename[0] == "":
            logger.warning("No file was selected")
        else:
            self.ReadData(filename[0])

    def OnSaveClicked(self):
        url = QtCore.QUrl('https://github.com/CBICA/NiBAx')
        QtGui.QDesktopServices.openUrl(url)

    def OnAboutClicked(self):
        self.aboutdialog.show()

    def OnCloseClicked(self):
        #close currently loaded data and model
        QtWidgets.QApplication.quit()

    def ResetUI(self):
        #reset all UI
        pass
