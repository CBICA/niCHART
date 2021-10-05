# This Python file uses the following encoding: utf-8
"""
contact: software@cbica.upenn.edu
Copyright (c) 2018 University of Pennsylvania. All rights reserved.
Use of this source code is governed by license located in license file: https://github.com/CBICA/BrainChart/blob/main/LICENSE
"""

from PyQt5 import QtCore, QtWidgets
#from PyQt5.QtWidgets import QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from BrainChart.dataio import DataIO
from BrainChart.datamodel import DataModel
from BrainChart.plotcanvas import PlotCanvas
import seaborn as sns
import BrainChart.processes
import struct
import pickle

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, dataFile=None, harmonizationModelFile=None, SPAREModelFile=None):
        super(MainWindow,self).__init__()
        self.SetupUi()
        self.SetupConnections()
        #defaults
        self.currentView = 'AgeTrend'
        #Instantiate data model
        self.model = DataModel()

        dio = DataIO()
        MUSEDictNAMEtoID, MUSEDictIDtoNAME = dio.ReadMUSEDictionary()
        self.model.SetMUSEDictionaries(MUSEDictNAMEtoID, MUSEDictIDtoNAME)

        if dataFile is not None:
            # if datafile provided on cmd line, load it
            self.OnDataFileOpenClicked(dataFile)
        if harmonizationModelFile is not None:
            #if harmonization model file provided on cmd line, load it
            self.OnHarmonizationModelFileOpenClicked(harmonizationModelFile)
        if SPAREModelFile is not None:
            #if SPARE model file provided on cmd line, load it
            self.OnSPAREModelFileOpenClicked(SPAREModelFile)

    def SetupConnections(self):
        self.actionOpenDataFile.triggered.connect(lambda: self.OnDataFileOpenClicked(None))
        self.actionOpenHarmonizationModelFile.triggered.connect(lambda: self.OnHarmonizationModelFileOpenClicked(None))
        self.actionOpenSPAREModelFile.triggered.connect(lambda: self.OnSPAREModelFileOpenClicked(None))
        self.comboBoxROI.currentIndexChanged.connect(self.UpdatePlot)
        self.comboBoxHue.currentIndexChanged.connect(self.UpdatePlot)
        self.actionQuitApplication.triggered.connect(self.OnQuitClicked)
        self.actionClose.triggered.connect(self.OnCloseClicked)
        self.actionSave.triggered.connect(self.OnSaveClicked)
        self.actionProcessSpare.triggered.connect(self.OnProcessSpareClicked)
        self.actionProcessHarmonization.triggered.connect(self.OnProcessHarmonizationClicked)
        self.actionGroupView.triggered.connect(self.OnViewChanged)

    def SetupUi(self):
        self.setObjectName("MainWindow")
        self.setWindowTitle("BrainChart Toolbox")
        self.resize(798, 593)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.setCentralWidget(self.centralwidget)

        self.layout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.layout.setObjectName("layout")

        self.leftPaneVLayout = QtWidgets.QVBoxLayout()
        self.leftPaneVLayout.setObjectName("leftPaneVLayout")

        self.dataStatisticsGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.dataStatisticsGroupBox.setObjectName("dataStatisticsGroupBox")
        self.leftPaneVLayout.addWidget(self.dataStatisticsGroupBox)

        self.dataStatsGroupBoxGridLayout = QtWidgets.QGridLayout(self.dataStatisticsGroupBox)

        #Add data statistics box on left pane
        #Data File
        self.label_DataFile = QtWidgets.QLabel(self.dataStatisticsGroupBox);
        self.label_DataFile.setObjectName("label_DataFile")
        self.label_DataFile.setText("Data File:")
        self.dataStatsGroupBoxGridLayout.addWidget(self.label_DataFile, 0, 0, 1, 1);

        self.label_DataFileValue = QtWidgets.QLabel(self.dataStatisticsGroupBox)
        self.label_DataFileValue.setObjectName("label_NumParticipantsValue")
        self.dataStatsGroupBoxGridLayout.addWidget(self.label_DataFileValue,0, 1, 1, 1)

        #Harmonization Model File
        self.label_HarmonizationModelFile = QtWidgets.QLabel(self.dataStatisticsGroupBox);
        self.label_HarmonizationModelFile.setObjectName("label_HarmonizationModelFile")
        self.label_HarmonizationModelFile.setText("Harmonization Model File:")
        self.dataStatsGroupBoxGridLayout.addWidget(self.label_HarmonizationModelFile, 1, 0, 1, 1);

        self.label_HarmonizationModelFileValue = QtWidgets.QLabel(self.dataStatisticsGroupBox)
        self.label_HarmonizationModelFileValue.setObjectName("label_HarmonizationModelFileValue")
        self.dataStatsGroupBoxGridLayout.addWidget(self.label_HarmonizationModelFileValue, 1, 1, 1, 1)

        #Participants
        self.label_NumParticipants = QtWidgets.QLabel(self.dataStatisticsGroupBox);
        self.label_NumParticipants.setObjectName("label_NumParticipants")
        self.label_NumParticipants.setText("Number of Participants:")
        self.dataStatsGroupBoxGridLayout.addWidget(self.label_NumParticipants, 2, 0, 1, 1);

        self.label_NumParticipantsValue = QtWidgets.QLabel(self.dataStatisticsGroupBox)
        self.label_NumParticipantsValue.setObjectName("label_NumParticipantsValue")
        self.dataStatsGroupBoxGridLayout.addWidget(self.label_NumParticipantsValue, 2, 1, 1, 1)

        #Observations
        self.label_NumObservations = QtWidgets.QLabel(self.dataStatisticsGroupBox);
        self.label_NumObservations.setObjectName("label_NumObservations")
        self.label_NumObservations.setText("Number of Observations:")
        self.dataStatsGroupBoxGridLayout.addWidget(self.label_NumObservations, 3, 0, 1, 1);

        self.label_NumObservationsValue = QtWidgets.QLabel(self.dataStatisticsGroupBox)
        self.label_NumObservationsValue.setObjectName("label_NumObservationsValue")
        self.dataStatsGroupBoxGridLayout.addWidget(self.label_NumObservationsValue, 3, 1, 1, 1)

        #Age
        self.label_Age = QtWidgets.QLabel(self.dataStatisticsGroupBox);
        self.label_Age.setObjectName("label_Age")
        self.label_Age.setText("Age [min, max]:")
        self.dataStatsGroupBoxGridLayout.addWidget(self.label_Age, 4, 0, 1, 1);

        self.label_AgeValue = QtWidgets.QLabel(self.dataStatisticsGroupBox)
        self.label_AgeValue.setObjectName("label_AgeValue")
        self.dataStatsGroupBoxGridLayout.addWidget(self.label_AgeValue, 4, 1, 1, 1)

        #Sex[M/F]
        self.label_Sex = QtWidgets.QLabel(self.dataStatisticsGroupBox);
        self.label_Sex.setObjectName("label_Sex")
        self.label_Sex.setText("Sex [M,F]:")
        self.dataStatsGroupBoxGridLayout.addWidget(self.label_Sex, 5, 0, 1, 1);

        self.label_SexValue = QtWidgets.QLabel(self.dataStatisticsGroupBox)
        self.label_SexValue.setObjectName("label_SexValue")
        self.dataStatsGroupBoxGridLayout.addWidget(self.label_SexValue, 5, 1, 1, 1)

        #add left pane to layout
        self.layout.addLayout(self.leftPaneVLayout)

        self.rightPaneVLayout = QtWidgets.QVBoxLayout()
        self.rightPaneVLayout.setObjectName("rightPaneVLayout")

        #add right pane to layout
        self.layout.addLayout(self.rightPaneVLayout)

        #plot parameters comboBox
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.comboBoxROI = QtWidgets.QComboBox(self.centralwidget)
        self.comboBoxROI.setObjectName("comboBoxROI")
        self.horizontalLayout_2.addWidget(self.comboBoxROI)
        self.comboBoxHue = QtWidgets.QComboBox(self.centralwidget)
        self.comboBoxHue.setObjectName("comboBoxHue")
        self.horizontalLayout_2.addWidget(self.comboBoxHue)
        self.rightPaneVLayout.addLayout(self.horizontalLayout_2)

        #instantiate plot canvas and add to UI layout
        self.plotCanvas = PlotCanvas(self)
        self.rightPaneVLayout.addWidget(self.plotCanvas)

        #menu bar
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 798, 22))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)

        self.menuFile = QtWidgets.QMenu("File",self.menubar)
        self.menuFile.setObjectName("menuFile")

        self.actionOpenDataFile = QtWidgets.QAction("Open Data File",self)
        self.actionOpenDataFile.setObjectName("actionOpen")
        self.menuFile.addAction(self.actionOpenDataFile)

        self.actionOpenHarmonizationModelFile = QtWidgets.QAction("Open Harmonization Model File",self)
        self.actionOpenHarmonizationModelFile.setObjectName("actionOpen")
        self.menuFile.addAction(self.actionOpenHarmonizationModelFile)

        self.actionOpenSPAREModelFile = QtWidgets.QAction("Open SPARE Model File",self)
        self.actionOpenSPAREModelFile.setObjectName("actionOpen")
        self.menuFile.addAction(self.actionOpenSPAREModelFile)

        self.actionSave = QtWidgets.QAction("Save",self)
        self.actionSave.setObjectName("actionSave")
        self.menuFile.addAction(self.actionSave)

        self.actionClose = QtWidgets.QAction("Close",self)
        self.actionClose.setObjectName("actionClose")
        self.menuFile.addAction(self.actionClose)

        self.actionQuitApplication = QtWidgets.QAction("Quit",self)
        self.actionQuitApplication.setObjectName("actionQuit")
        self.menuFile.addAction(self.actionQuitApplication)

        self.menuProcess = QtWidgets.QMenu("Process",self.menubar)
        self.menuProcess.setObjectName("menuProcess")

        self.actionProcessSpare = QtWidgets.QAction("Compute SPARE-*",self)
        self.actionProcessSpare.setObjectName("actionSpare")
        self.menuProcess.addAction(self.actionProcessSpare)

        self.actionProcessHarmonization = QtWidgets.QAction("Harmonization",self)
        self.actionProcessHarmonization.setObjectName("actionHarmonization")
        self.menuProcess.addAction(self.actionProcessHarmonization)

        self.menuView = QtWidgets.QMenu("View",self.menubar)
        self.menuView.setObjectName("menuView")

        self.actionViewAgeTrend = QtWidgets.QAction("AgeTrend",self)
        self.actionViewAgeTrend.setObjectName("actionViewAgeTrend")
        self.menuView.addAction(self.actionViewAgeTrend)

        self.actionSPARE = QtWidgets.QAction("SPARE",self)
        self.actionSPARE.setObjectName("actionSPARE")
        self.menuView.addAction(self.actionSPARE)

        self.actionGroupView = QtWidgets.QActionGroup(self)
        self.actionGroupView.addAction(self.actionViewAgeTrend)
        self.actionGroupView.addAction(self.actionSPARE)

        self.menuHelp = QtWidgets.QMenu("Help",self.menubar)
        self.menuHelp.setObjectName("menuHelp")

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuProcess.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())


    def OnDataFileOpenClicked(self,dataFile=None):

        #when there is already some data loaded, we get a confirmation from the user
        #to close the loaded data and load a new one
        if(self.model.IsValidData()):
            returnValue = QtWidgets.QMessageBox.question(self,
            'Warning',
            "There is already a data loaded. Do you want to close this data and load new one?")
            if(returnValue == QtWidgets.QMessageBox.Yes):
                self.OnCloseClicked()
            elif(returnValue == QtWidgets.QMessageBox.No):
                return

        #when there is no data loaded or when the loaded data was closed to load a new one
        if dataFile is None:
            filename = QtWidgets.QFileDialog.getOpenFileName(self,
            'Open data file',
            QtCore.QDir().homePath(),
            "Pickle files (*.pkl.gz)")
        else:
            filename = [dataFile]

        if not filename[0]:
            return

        #read input data
        dio = DataIO()
        d = dio.ReadPickleFile(filename[0])

        #set data in model
        self.model.SetData(d)
        self.model.SetDataFilePath(filename[0])

        #populate data statistics
        self.UpdateDataStatistics()

        #populate the ROI only if the data is valid
        #Otherwise, show error message
        if(self.model.IsValidData()):
            self.PopulateROI()
            self.PopulateHue()
        else:
            QtWidgets.QMessageBox.critical(self,
            'Error',
            "Invalid Input Data. Please check the data and try again.",
            QtWidgets.QMessageBox.Ok)


    def OnHarmonizationModelFileOpenClicked(self, harmonizationModelFile=None):

        if harmonizationModelFile is None:
            filename = QtWidgets.QFileDialog.getOpenFileName(self,
            'Open iSTAGING model file',
            QtCore.QDir().homePath(),
            "Pickle files (*.pkl)")
        else:
            filename = [harmonizationModelFile]

        if not filename[0]:
            return

        #read input data
        dio = DataIO()
        m = dio.ReadPickleFile(filename[0])

        #set data in model
        self.model.SetHarmonizationModel(m)
        self.model.SetHarmonizationModelFilePath(filename[0])

        #populate data statistics
        self.UpdateDataStatistics()

        #populate the ROI only if the data is valid
        #Otherwise, show error message
        if(self.model.IsValidData()):
            self.PopulateROI()
            self.PopulateHue()
        else:
            QtWidgets.QMessageBox.critical(self,
            'Error',
            "Invalid Input Data [Harmonization]. Please check the data and try again.",
            QtWidgets.QMessageBox.Ok)


    def OnSPAREModelFileOpenClicked(self, SPAREModelFile=None):

        if SPAREModelFile is None:
            filename = QtWidgets.QFileDialog.getOpenFileName(self,
            'Open iSTAGING SPARE-* model file',
            QtCore.QDir().homePath(),
            "Pickle files (*.pkl.gz)")
        else:
            filename = [SPAREModelFile]

        if not filename[0]:
            return

        #read input data
        dio = DataIO()
        BrainAgeModel, ADModel = dio.ReadSPAREModel(filename[0])

        #set data in model
        self.model.SetSPAREModel(BrainAgeModel, ADModel)

        #populate the ROI only if the data is valid
        #Otherwise, show error message
        if(self.model.IsValidData()):
            self.PopulateROI()
            self.PopulateHue()
        else:
            QtWidgets.QMessageBox.critical(self,
            'Error',
            "Invalid Input Data [SPARE]. Please check the data and try again.",
            QtWidgets.QMessageBox.Ok)


    def UpdatePlot(self):

        #get current selected combobox item
        currentROI = self.comboBoxROI.currentText()
        currentHue = self.comboBoxHue.currentText()


        # Translate ROI name back to ROI ID
        MUSEDictNAMEtoID, _ = self.model.GetMUSEDictionaries()
        if currentROI.startswith('(MUSE)'):
            currentROI = list(map(MUSEDictNAMEtoID.get, [currentROI[7:]]))[0]

        if currentROI.startswith('(Harmonized MUSE)'):
            currentROI = 'H_' + list(map(MUSEDictNAMEtoID.get, [currentROI[18:]]))[0]

        if currentROI.startswith('(WMLS)'):
            currentROI = list(map(MUSEDictNAMEtoID.get, [currentROI[7:]]))[0].replace('MUSE_', 'WMLS_')


        #create empty dictionary of plot options
        plotOptions = dict()

        #fill dictionary with options
        plotOptions['ROI'] = currentROI
        plotOptions['HUE'] = currentHue
        plotOptions['VIEW'] = self.currentView

        #Plot data
        self.plotCanvas.Plot(self.model,plotOptions)

    def PopulateROI(self):
        #get data column header names
        datakeys = self.model.GetColumnHeaderNames()

        #construct ROI list to populate comboBox
        roiList = (  [x for x in datakeys if x.startswith('MUSE_Volume')]
                   + [x for x in datakeys if x.startswith('H_MUSE_Volume')]
                   + [x for x in datakeys if x.startswith('WMLS_Volume')]
                   + [x for x in datakeys if x.startswith('H_WMLS_Volume')]
                   + ['SPARE_AD','SPARE_BA','Non-existing-ROI','DLICV'])
        
        # !!! remove ROI with no dictionary entry
        if 'WMLS_Volume_43' in roiList:
            roiList.remove('WMLS_Volume_43')

        if 'WMLS_Volume_42' in roiList:
            roiList.remove('WMLS_Volume_42')
        
        if 'WMLS_Volume_69' in roiList:
            roiList.remove('WMLS_Volume_69')


        _, MUSEDictIDtoNAME = self.model.GetMUSEDictionaries()
        roiList = list(set(roiList).intersection(set(datakeys)))
        roiList.sort()
        roiList = ['(MUSE) ' + list(map(MUSEDictIDtoNAME.get, [k]))[0] if k.startswith('MUSE_') else k for k in roiList]
        roiList = ['(Harmonized MUSE) ' + list(map(MUSEDictIDtoNAME.get, [k[2:]]))[0] if k.startswith('H_MUSE_') else k for k in roiList]
        roiList = ['(WMLS) ' + list(map(MUSEDictIDtoNAME.get, [k.replace('WMLS_', 'MUSE_')]))[0] if k.startswith('WMLS_') else k for k in roiList]

        #add the list items to comboBox
        self.comboBoxROI.blockSignals(True)
        self.comboBoxROI.clear()
        self.comboBoxROI.blockSignals(False)
        self.comboBoxROI.addItems(roiList)


    def PopulateHue(self):
        #add the list items to comboBoxHue
        datakeys = self.model.GetColumnHeaderNames()
        categoryList = ['Sex','Study','A','T','N','PIB_Status']
        categoryList = list(set(categoryList).intersection(set(datakeys)))
        self.comboBoxROI.blockSignals(True)
        self.comboBoxHue.clear()
        self.comboBoxROI.blockSignals(False)

        self.comboBoxHue.addItems(categoryList)

    def OnQuitClicked(self):
        #quit application
        QtWidgets.QApplication.quit()

    def OnCloseClicked(self):
        #close currently loaded data and model
        self.ResetUI()
        self.model.Reset()

    def OnSaveClicked(self):
        #save currently loaded data
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self,
        'Save iSTAGING data file',
        QtCore.QDir().homePath(),
        "Pickle Files (*.pkl.gz)")

        if not fileName:
            return

        #save data
        dio = DataIO()
        dio.SavePickleFile(self.model.GetCompleteData(),fileName)

    def ResetUI(self):
        #reset all UI

        #clear plot
        self.plotCanvas.Reset()

        #clear ROI & HUE comboboxes
        self.comboBoxROI.blockSignals(True)
        self.comboBoxHue.blockSignals(True)

        self.comboBoxHue.clear()
        self.comboBoxROI.clear()

        self.comboBoxROI.blockSignals(False)
        self.comboBoxHue.blockSignals(False)

        #clear data statistics on left pane
        self.label_NumParticipantsValue.setText("")
        self.label_NumObservationsValue.setText("")
        self.label_AgeValue.setText("")
        self.label_SexValue.setText("")

    def UpdateDataStatistics(self):
        #get data statistics from model
        stats = self.model.GetDataStatistics()

        #add statistics values to UI
        self.label_NumParticipantsValue.setText(str(stats['numParticipants']))
        self.label_NumObservationsValue.setText(str(stats['numObservations']))
        ageVal = "[" + str(round(stats['minAge'],2)) + "," + str(round(stats['maxAge'],2)) + "]"
        self.label_AgeValue.setText(ageVal)
        sexVal = "[" + str(stats['countsPerSex']['M']) + "," + str(stats['countsPerSex']['F']) + "]"
        self.label_SexValue.setText(sexVal)

        dataFilePath = self.model.GetDataFilePath()
        harmonizationModelFilePath = self.model.GetHarmonizationModelFilePath()
        self.label_DataFileValue.setText(QtCore.QFileInfo(dataFilePath).fileName())
        self.label_DataFileValue.setToolTip(QtCore.QFileInfo(dataFilePath).absoluteFilePath())
        self.label_HarmonizationModelFileValue.setText(QtCore.QFileInfo(harmonizationModelFilePath).fileName())
        self.label_HarmonizationModelFileValue.setToolTip(QtCore.QFileInfo(harmonizationModelFilePath).absoluteFilePath())

    def OnProcessSpareClicked(self):
        p = BrainChart.processes.Processes()
        if (self.model.ADModel is not None and
           self.model.BrainAgeModel is not None):
            self.model.SetData(p.DoSPARE(self.model.GetCompleteData(),
                                        self.model.ADModel,
                                        self.model.BrainAgeModel))
            self.PopulateROI()
        else:
            print('No SPARE-* models loaded.')


    def OnProcessHarmonizationClicked(self):
        #TODO: show msg if no harmonization model is loaded
        p = BrainChart.processes.Processes()
        if (self.model.harmonization_model is not None):
            self.model.SetData(p.DoHarmonization(self.model.GetCompleteData(),
                                                self.model.harmonization_model))
            self.PopulateROI()
        else:
            print('No harmonization model loaded.')


    def OnViewChanged(self,action):
        #update current view
        self.currentView = action.text()

        #control combo box visibility for views
        if(action.text() == 'SPARE'):
            self.comboBoxROI.hide()
        elif(action.text() == 'AgeTrend'):
            self.comboBoxROI.show()

        #redraw plot
        self.UpdatePlot()
