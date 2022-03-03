from PyQt5.QtGui import *
from PyQt5 import QtGui, QtCore, QtWidgets, uic
import sys, os
import pandas as pd
from NiBAx.plugins.loadsave.dataio import DataIO
# import dtale
from NiBAx.core.baseplugin import BasePlugin
from NiBAx.core import iStagingLogger

logger = iStagingLogger.get_logger(__name__)

class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data
        self.header_labels = None

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        self.header_labels = self._data.keys()
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            return self.header_labels[section]
        return QtCore.QAbstractTableModel.headerData(self, section, orientation, role)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(str(
                    self._data.iloc[index.row()][index.column()]))
        return QtCore.QVariant()


class LoadSave(QtWidgets.QWidget,BasePlugin):

    def __init__(self):
        super(LoadSave,self).__init__()
        self.datamodel = None
        root = os.path.dirname(__file__)
        self.readAdditionalInformation(root)
        self.ui = uic.loadUi(os.path.join(root, 'loadsave.ui'),self)
        self.dataView = QtWidgets.QTableView()
        self.ui.verticalLayout_2.addWidget(self.dataView)

        # WORKAROUND: Deactivate explore button
        self.ui.dtale_Btn.setVisible(False)


    def SetupConnections(self):
        self.ui.open_data_file_Btn.clicked.connect(lambda: self.OnOpenDataFileBtnClicked())
        self.datamodel.data_changed.connect(lambda: self.OnDataChanged())
        self.ui.save_data_Btn.clicked.connect(lambda: self.OnSaveDataBtClicked())
        self.ui.dtale_Btn.clicked.connect(lambda: self.OnDtaleBtnClicked())


    def OnDtaleBtnClicked(self):
        if ('level_0' in self.datamodel.data.keys()):
            self.datamodel.data.drop('level_0', axis=1, inplace=True)
        d = dtale.show(self.datamodel.data.reset_index(drop=True))
        d.open_browser()


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


    def PopulateTable(self):
        model = PandasModel(self.datamodel.data.head(20))
        self.dataView.setModel(model)

    def OnDataChanged(self):
        self.PopulateTable()

    def ReadData(self,filename):
        #read input data
        dio = DataIO()
        d = dio.ReadPickleFile(filename)

        logger.info('New data read from file: %s', filename)

        #also read MUSE dictionary
        MUSEDictNAMEtoID, MUSEDictIDtoNAME, MUSEDictDataFrame = dio.ReadMUSEDictionary()
        self.datamodel.SetMUSEDictionaries(MUSEDictNAMEtoID, MUSEDictIDtoNAME,MUSEDictDataFrame)

        #also read Derived MUSE dictionary 
        DerivedMUSEMap = dio.ReadDerivedMUSEMap()
        self.datamodel.SetDerivedMUSEMap(DerivedMUSEMap)

        #set data in model
        self.datamodel.SetDataFilePath(filename)
        self.datamodel.SetData(d)

