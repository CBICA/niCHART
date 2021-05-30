# This Python file uses the following encoding: utf-8
"""
contact: software@cbica.upenn.edu
Copyright (c) 2018 University of Pennsylvania. All rights reserved.
Use of this source code is governed by license located in license file: https://github.com/CBICA/iSTAGING-Tools/blob/main/LICENSE
"""

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from dataio import DataIO
from datamodel import DataModel
import seaborn as sns

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.SetupUi()
        self.SetupConnections()
        self.model = DataModel()

    def SetupConnections(self):
        self.actionOpen.triggered.connect(self.OnFileOpenClicked)
        self.comboBoxROI.currentIndexChanged.connect(self.UpdatePlot)

    def SetupUi(self):
        self.setObjectName("MainWindow")
        self.setWindowTitle("MainWindow")
        self.resize(798, 593)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.setCentralWidget(self.centralwidget)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")

        self.label = QtWidgets.QLabel("Plot",self.centralwidget)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)

        #plot parameters comboBox
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.comboBoxROI = QtWidgets.QComboBox(self.centralwidget)
        self.comboBoxROI.setObjectName("comboBoxROI")
        self.horizontalLayout_2.addWidget(self.comboBoxROI)
        self.radioButton = QtWidgets.QRadioButton("Population Average",self.centralwidget)
        self.radioButton.setObjectName("radioButton")
        self.horizontalLayout_2.addWidget(self.radioButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        #plot widget
        # a figure instance to plot on
        self.figure = Figure()
        # this is the Canvas Widget that displays the `figure`
        self.canvas = FigureCanvas(self.figure)
        self.verticalLayout.addWidget(self.canvas)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton = QtWidgets.QPushButton("Ok",self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)

        #menu bar
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 798, 22))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)

        self.menuFile = QtWidgets.QMenu("File",self.menubar)
        self.menuFile.setObjectName("menuFile")

        self.actionOpen = QtWidgets.QAction("Open",self)
        self.actionOpen.setObjectName("actionOpen")
        self.menuFile.addAction(self.actionOpen)

        self.menuProcess = QtWidgets.QMenu("Process",self.menubar)
        self.menuProcess.setObjectName("menuProcess")

        self.menuHelp = QtWidgets.QMenu("Help",self.menubar)
        self.menuHelp.setObjectName("menuHelp")

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuProcess.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())


    def OnFileOpenClicked(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file','c:\\',"Pickle files (*.pkl.gz)")

        #read input data
        dio = DataIO()
        d = dio.ReadPickleFile(fname[0])

        #set data in model
        self.model.SetData(d)

        #populate the ROI only if the data is valid
        #Otherwise, show error message
        if(self.model.IsValid()):
            self.PopulateROI()
        else:
            QMessageBox.critical(self, 'Error', "Invalid Input Data. Please check the data and try again.", QMessageBox.Ok)


    def UpdatePlot(self):

        #get current selected combobox item
        currentROI = self.comboBoxROI.currentText()

        # clear plot
        self.figure.clear()

        # create an axis
        ax = self.figure.add_subplot(111)

        #seaborn plot on axis
        sns.scatterplot(x='Age', y=currentROI, data=self.model.GetData(currentROI,"Sex"), hue='Sex',ax=ax)

        # refresh canvas
        self.canvas.draw()

    def PopulateROI(self):
        #get data column header names
        datakeys = self.model.GetColumnHeaderNames()

        #construct ROI list to populate comboBox
        roiList = [x for x in datakeys if x.startswith('MUSE_Volume')]

        #add the list items to comboBox
        self.comboBoxROI.addItems(roiList)

