from PyQt5.QtGui import *
from yapsy.IPlugin import IPlugin
from PyQt5 import QtGui, QtCore, QtWidgets, uic
import sys, os
from QtBrainChartGUI.plugins.data.dataio import DataIO

class Data(QtWidgets.QWidget,IPlugin):

    def __init__(self):
        super(Data,self).__init__()
        self.datamodel = None
        root = os.path.dirname(__file__)
        self.ui = uic.loadUi(os.path.join(root, 'data.ui'),self)

    def SetupConnections(self):
        self.ui.browseBtn.clicked.connect(lambda: self.OnBrowseBtnClicked())
        self.datamodel.data_changed.connect(lambda: self.OnDataChanged())

    def OnBrowseBtnClicked(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(None,
        'Open data file',
        QtCore.QDir().homePath(),
        "Pickle files (*.pkl.gz)")

        #read input data
        dio = DataIO()
        d = dio.ReadPickleFile(filename[0])

        #set data in model
        self.datamodel.SetData(d)

    def PopulateTable(self):
        df = self.datamodel.GetCompleteData()
        colNames = self.datamodel.GetColumnHeaderNames()

        self.ui.tableWidget.setColumnCount(len(df.columns))
        self.ui.tableWidget.setRowCount(len(df.index))
        #for i in range(len(df.index)):
        for i in range(5):
            for j in range(len(df.columns)):
                self.ui.tableWidget.setItem(i,j,QtWidgets.QTableWidgetItem(str(df.iloc[i, j])))

        self.ui.tableWidget.setHorizontalHeaderLabels(colNames)

    def OnDataChanged(self):
        self.PopulateTable()
