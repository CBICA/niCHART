# This Python file uses the following encoding: utf-8
"""
contact: software@cbica.upenn.edu
Copyright (c) 2018 University of Pennsylvania. All rights reserved.
Use of this source code is governed by license located in license file: https://github.com/CBICA/iSTAGING-Tools/blob/main/LICENSE
"""

from PyQt5 import QtCore, QtWidgets
#from PyQt5.QtWidgets import QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from iSTAGING.dataio import DataIO
from iSTAGING.datamodel import DataModel
import seaborn as sns

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, DataFile=None, HarmonizationModelFile=None):
        super(MainWindow,self).__init__()
        self.SetupUi()
        self.SetupConnections()
        self.model = DataModel(DataFile=DataFile,
                               HarmonizationModelFile=HarmonizationModelFile)
        if DataFile is not None:
            #populate the ROI only if the data is valid
            #Otherwise, show error message
            if(self.model.IsValid()):
                self.PopulateROI()
                self.PopulateHue()
            else:
                QtWidgets.QMessageBox.critical(self,
                'Error',
                "Invalid Input Data. Please check the data and try again.",
                QtWidgets.QMessageBox.Ok)


    def SetupConnections(self):
        self.actionOpenDataFile.triggered.connect(self.OnDataFileOpenClicked)
        self.actionOpenModelFile.triggered.connect(self.OnModelFileOpenClicked)
        self.comboBoxROI.currentIndexChanged.connect(self.UpdatePlot)
        self.comboBoxHue.currentIndexChanged.connect(self.UpdatePlot)
        self.actionQuitApplication.triggered.connect(self.OnQuitClicked)
        self.actionClose.triggered.connect(self.OnCloseClicked)

    def SetupUi(self):
        self.setObjectName("MainWindow")
        self.setWindowTitle("iSTAGING Data Visualization and Extraction")
        self.resize(798, 593)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.setCentralWidget(self.centralwidget)

        self.layout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.layout.setObjectName("layout")

        self.leftPaneVLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.leftPaneVLayout.setObjectName("leftPaneVLayout")

        self.dataStatisticsGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.dataStatisticsGroupBox.setObjectName("dataStatisticsGroupBox")
        self.leftPaneVLayout.addWidget(self.dataStatisticsGroupBox)

        self.dataStatsGroupBoxGridLayout = QtWidgets.QGridLayout(self.dataStatisticsGroupBox)

        #Add data statistics box on left pane
        #Participants
        self.label_NumParticipants = QtWidgets.QLabel(self.dataStatisticsGroupBox);
        self.label_NumParticipants.setObjectName("label_NumParticipants")
        self.label_NumParticipants.setText("Number of Participants:")
        self.dataStatsGroupBoxGridLayout.addWidget(self.label_NumParticipants, 0, 0, 1, 1);

        self.label_NumParticipantsValue = QtWidgets.QLabel(self.dataStatisticsGroupBox)
        self.label_NumParticipantsValue.setObjectName("label_NumParticipantsValue")
        self.dataStatsGroupBoxGridLayout.addWidget(self.label_NumParticipantsValue, 0, 1, 1, 1)

        #Observations
        self.label_NumObservations = QtWidgets.QLabel(self.dataStatisticsGroupBox);
        self.label_NumObservations.setObjectName("label_NumObservations")
        self.label_NumObservations.setText("Number of Observations:")
        self.dataStatsGroupBoxGridLayout.addWidget(self.label_NumObservations, 1, 0, 1, 1);

        self.label_NumObservationsValue = QtWidgets.QLabel(self.dataStatisticsGroupBox)
        self.label_NumObservationsValue.setObjectName("label_NumObservationsValue")
        self.dataStatsGroupBoxGridLayout.addWidget(self.label_NumObservationsValue, 1, 1, 1, 1)

        #Age
        self.label_Age = QtWidgets.QLabel(self.dataStatisticsGroupBox);
        self.label_Age.setObjectName("label_Age")
        self.label_Age.setText("Age [min, max]:")
        self.dataStatsGroupBoxGridLayout.addWidget(self.label_Age, 2, 0, 1, 1);

        self.label_AgeValue = QtWidgets.QLabel(self.dataStatisticsGroupBox)
        self.label_AgeValue.setObjectName("label_AgeValue")
        self.dataStatsGroupBoxGridLayout.addWidget(self.label_AgeValue, 2, 1, 1, 1)

        #Sex[M/F]
        self.label_Sex = QtWidgets.QLabel(self.dataStatisticsGroupBox);
        self.label_Sex.setObjectName("label_Sex")
        self.label_Sex.setText("Sex [M/F]:")
        self.dataStatsGroupBoxGridLayout.addWidget(self.label_Sex, 3, 0, 1, 1);

        self.label_SexValue = QtWidgets.QLabel(self.dataStatisticsGroupBox)
        self.label_SexValue.setObjectName("label_SexValue")
        self.dataStatsGroupBoxGridLayout.addWidget(self.label_SexValue, 3, 1, 1, 1)

        #add left pane to layout
        self.layout.addLayout(self.leftPaneVLayout)

        self.rightPaneVLayout = QtWidgets.QVBoxLayout(self.centralwidget)
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
        self.radioButton = QtWidgets.QRadioButton("Population Average",self.centralwidget)
        self.radioButton.setObjectName("radioButton")
        self.horizontalLayout_2.addWidget(self.radioButton)
        self.rightPaneVLayout.addLayout(self.horizontalLayout_2)

        #plot widget
        # a figure instance to plot on
        self.figure = Figure()
        # this is the Canvas Widget that displays the `figure`
        self.canvas = FigureCanvas(self.figure)
        self.rightPaneVLayout.addWidget(self.canvas)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton = QtWidgets.QPushButton("Ok",self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.rightPaneVLayout.addLayout(self.horizontalLayout)

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

        self.actionOpenModelFile = QtWidgets.QAction("Open Model File",self)
        self.actionOpenModelFile.setObjectName("actionOpen")
        self.menuFile.addAction(self.actionOpenModelFile)

        self.actionClose = QtWidgets.QAction("Close",self)
        self.actionClose.setObjectName("actionClose")
        self.menuFile.addAction(self.actionClose)

        self.actionQuitApplication = QtWidgets.QAction("Quit",self)
        self.actionQuitApplication.setObjectName("actionQuit")
        self.menuFile.addAction(self.actionQuitApplication)

        self.menuProcess = QtWidgets.QMenu("Process",self.menubar)
        self.menuProcess.setObjectName("menuProcess")

        self.menuHelp = QtWidgets.QMenu("Help",self.menubar)
        self.menuHelp.setObjectName("menuHelp")

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuProcess.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())


    def OnDataFileOpenClicked(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(self,
        'Open data file',
        QtCore.QDir().homePath(),
        "Pickle files (*.pkl.gz)")

        if not filename[0]:
            return

        #read input data
        dio = DataIO()
        d = dio.ReadPickleFile(filename[0])

        #set data in model
        self.model.SetData(d)

        #populate data statistics
        self.UpdateDataStatistics()

        #populate the ROI only if the data is valid
        #Otherwise, show error message
        if(self.model.IsValid()):
            self.PopulateROI()
            self.PopulateHue()
        else:
            QtWidgets.QMessageBox.critical(self,
            'Error',
            "Invalid Input Data. Please check the data and try again.",
            QtWidgets.QMessageBox.Ok)


    def OnModelFileOpenClicked(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(self,
        'Open iSTAGING model file',
        QtCore.QDir().homePath(),
        "Pickle files (*.pkl)")

        if not filename[0]:
            return

        #read input data
        dio = DataIO()
        m = dio.ReadPickleFile(filename[0])

        #set data in model
        self.model.SetHarmonizationModel(m)

        #populate the ROI only if the data is valid
        #Otherwise, show error message
        if(self.model.IsValid()):
            self.PopulateROI()
            self.PopulateHue()
        else:
            QtWidgets.QMessageBox.critical(self,
            'Error',
            "Invalid Input Data. Please check the data and try again.",
            QtWidgets.QMessageBox.Ok)


    def UpdatePlot(self):

        #get current selected combobox item
        currentROI = self.comboBoxROI.currentText()
        currentHue = self.comboBoxHue.currentText()
        if not currentHue:
            currentHue = 'Sex'

        # clear plot
        self.figure.clear()

        # create an axis
        ax = self.figure.add_subplot(111)

        # seaborn plot on axis
        sns.scatterplot(x='Age', y=currentROI,  hue=currentHue,ax=ax, s=5,
                       data=self.model.GetData(currentROI,currentHue))
        
        # Plot normative range if according GAM model is available
        if (self.model.harmonization_model is not None) and (currentROI in self.model.harmonization_model['ROIs']):
            x,y,z = self.model.GetNormativeRange(currentROI)
            print('Pooled variance: %f' % (z))
            # Plot three lines as expected mean and +/- 2 times standard deviation
            sns.lineplot(x=x, y=y, ax=ax, linestyle='-', markers=False, color='k')
            sns.lineplot(x=x, y=y+z, ax=ax, linestyle=':', markers=False, color='k')
            sns.lineplot(x=x, y=y-z, ax=ax, linestyle=':', markers=False, color='k')

        # refresh canvas
        self.canvas.draw()

    def PopulateROI(self):
        #get data column header names
        datakeys = self.model.GetColumnHeaderNames()

        #construct ROI list to populate comboBox
        roiList = (  [x for x in datakeys if x.startswith('MUSE_Volume')]
                   + [x for x in datakeys if x.startswith('H_MUSE_Volume')]
                   + [x for x in datakeys if x.startswith('WMLS_Volume')]
                   + [x for x in datakeys if x.startswith('H_WMLS_Volume')]
                   + ['SPARE_AD','SPARE_BA','Non-existing-ROI','DLICV'])
        roiList = list(set(roiList).intersection(set(datakeys)))
        roiList.sort()

        #add the list items to comboBox
        self.comboBoxROI.addItems(roiList)


    def PopulateHue(self):
        #add the list items to comboBoxHue
        datakeys = self.model.GetColumnHeaderNames()
        categoryList = ['Sex','Study','A','T','N','PIB_Status']
        categoryList = list(set(categoryList).intersection(set(datakeys)))
        self.comboBoxHue.addItems(categoryList)

    def OnQuitClicked(self):
        #quit application
        QtWidgets.QApplication.quit()

    def OnCloseClicked(self):
        #close currently loaded data and model
        self.ResetUI()
        self.model.Reset()

    def ResetUI(self):
        #reset all UI

        #clear plot
        self.figure.clear()

        # refresh canvas
        self.canvas.draw()

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
