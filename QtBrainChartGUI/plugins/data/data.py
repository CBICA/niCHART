from PyQt5.QtGui import *
from yapsy.IPlugin import IPlugin
from PyQt5 import QtGui, QtCore, QtWidgets, uic
import sys, os
import pandas as pd
from QtBrainChartGUI.plugins.data.dataio import DataIO

class Data(QtWidgets.QWidget,IPlugin):

    def __init__(self):
        super(Data,self).__init__()
        self.datamodel = None
        root = os.path.dirname(__file__)
        self.ui = uic.loadUi(os.path.join(root, 'data.ui'),self)


    def SetupConnections(self):
        self.ui.open_data_file_Btn.clicked.connect(lambda: self.OnOpenDataFileBtnClicked())
        self.datamodel.data_changed.connect(lambda: self.OnDataChanged())
        self.ui.save_data_Btn.clicked.connect(lambda: self.OnSaveDataBtClicked())


    def OnSaveDataBtClicked(self):
        filename = QtWidgets.QFileDialog.getSaveFileName(None,
            'Save data frame to file',
            QtCore.QDir().homePath(),
            "Pickle files (*.pkl.gz *.pkl)")

        if filename[0] == "":
            print("No file was selected")
        else:
            pd.to_pickle(self.datamodel.data, filename[0])


    def OnOpenDataFileBtnClicked(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(None,
        'Open data file',
        QtCore.QDir().homePath(),
        "Pickle files (*.pkl.gz *.pkl)")

        if filename[0] == "":
            print("No data was selected")
        else:
            file = pd.read_pickle(filename[0])
            if not (isinstance(file,pd.DataFrame)):
                print('Selected file must be a dataframe.')
            else:
                self.ReadData(filename[0])
            self.ui.tableWidget
        self.ui.tableWidget


    def PopulateTable(self):
        df = self.datamodel.GetCompleteData()
        colNames = self.datamodel.GetColumnHeaderNames()

        self.ui.tableWidget.setColumnCount(len(df.columns))
        self.ui.tableWidget.setRowCount(len(df.index))
        #for i in range(len(df.index)):
        for i in range(20):
            for j in range(len(df.columns)):
                self.ui.tableWidget.setItem(i,j,QtWidgets.QTableWidgetItem(str(df.iloc[i, j])))

        self.ui.tableWidget.setHorizontalHeaderLabels(colNames)

    def OnDataChanged(self):
        pass
        #self.PopulateTable()

    def ReadData(self,filename):
        #read input data
        dio = DataIO()
        d = dio.ReadPickleFile(filename)

        #also read MUSE dictionary
        MUSEDictNAMEtoID, MUSEDictIDtoNAME = dio.ReadMUSEDictionary()
        self.datamodel.SetMUSEDictionaries(MUSEDictNAMEtoID, MUSEDictIDtoNAME)

        #set data in model
        self.datamodel.SetDataFilePath(filename)
        self.datamodel.SetData(d)

