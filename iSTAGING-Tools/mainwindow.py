# This Python file uses the following encoding: utf-8
"""
contact: software@cbica.upenn.edu
Copyright (c) 2018 University of Pennsylvania. All rights reserved.
Use of this source code is governed by license located in license file: https://github.com/CBICA/iSTAGING-Tools/blob/main/LICENSE
"""

from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from dataio import DataIO
from pathlib import Path
import seaborn as sns

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.SetupUi()
        self.SetupConnections()

    def SetupConnections(self):
        self.actionOpen.triggered.connect(self.OnFileOpenClicked)

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
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setObjectName("comboBox")
        self.horizontalLayout_2.addWidget(self.comboBox)
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
        #fname = Path("D://ashish//Data//iSTAGINGData//istaging.pkl.gz")
        #fname = Path("D://ashish//Data//iSTAGINGData//short.pkl.gz")
        dio = DataIO()
        pkldata = dio.ReadPickleFile(fname[0])

        #pkldata.sample(5000).to_pickle("D:/ashish/Data/iSTAGINGData/short.pkl.gz")

        # clear plot
        self.figure.clear()

        # create an axis
        ax = self.figure.add_subplot(111)

        # plot data
        #ax.plot(data, '*-')
        #pkldata.plot(kind='scatter',x='Age',y='MUSE_Volume_47',color='red',ax=ax)
        #ax.plot('Age','MUSE_Volume_47',data=pkldata, color='red')
        sns.scatterplot(x='Age', y='MUSE_Volume_47', data=pkldata, hue='Sex',ax=ax)

        # refresh canvas
        self.canvas.draw()
