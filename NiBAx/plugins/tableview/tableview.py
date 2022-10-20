from PyQt5.QtGui import *
from PyQt5 import QtGui, QtCore, QtWidgets, uic
import sys, os
import pandas as pd
from NiBAx.core.dataio import DataIO
# import dtale
from NiBAx.core.baseplugin import BasePlugin
from NiBAx.core import iStagingLogger
from NiBAx.core.gui.SearchableQComboBox import SearchableQComboBox
from NiBAx.core.gui.CheckableQComboBox import CheckableQComboBox

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

class TableView(QtWidgets.QWidget,BasePlugin):

    def __init__(self):
        super(TableView,self).__init__()
        self.datamodel = None
        root = os.path.dirname(__file__)
        self.readAdditionalInformation(root)
        self.ui = uic.loadUi(os.path.join(root, 'tableview.ui'),self)
        
        self.dataView = QtWidgets.QTableView()
        self.ui.vlA.addWidget(self.dataView)

        self.ui.comboBoxSort1 = SearchableQComboBox(self.ui)
        self.ui.vlBBAA.addWidget(self.ui.comboBoxSort1)

        self.ui.comboBoxSort2 = SearchableQComboBox(self.ui)
        self.ui.vlBBBA.addWidget(self.ui.comboBoxSort2)

        #self.ui.comboBoxSelect = SearchableQComboBox(self.ui)
        self.ui.comboBoxSelect = CheckableQComboBox(self.ui)
        self.ui.vlBAA.addWidget(self.ui.comboBoxSelect)

        self.ui.wB.setMaximumWidth(300)

        # WORKAROUND: Deactivate explore button
        #self.ui.dtale_Btn.setVisible(False)
        
        #self.ui.vlB.addStretch()
        #self.ui.vlBAB.addStretch()


    def SetupConnections(self):
        self.ui.selBtn.clicked.connect(lambda: self.OnSelBtnClicked())
        self.ui.sortBtn.clicked.connect(lambda: self.OnSortBtnClicked())
        self.datamodel.data_changed.connect(lambda: self.OnDataChanged())
        self.datamodel.currdata_changed.connect(lambda: self.OnCurrDataChanged())


    def OnSortBtnClicked(self):
        sortCols = []
        sortOrders = []

        if self.ui.check_sort1.isChecked():
            sortCols.append(self.ui.comboBoxSort1.currentText())
            if self.ui.check_asc1.isChecked():
                sortOrders.append(True)
            else:
                sortOrders.append(False)
        
        if self.ui.check_sort2.isChecked():
            sortCols.append(self.ui.comboBoxSort2.currentText())
            if self.ui.check_asc2.isChecked():
                sortOrders.append(True)
            else:
                sortOrders.append(False)
        self.datamodel.sortCols = sortCols
        self.datamodel.sortOrders = sortOrders
        self.PopulateTable()

    def OnSelBtnClicked(self):
        selCols = self.ui.comboBoxSelect.listCheckedItems()
        dtmp = self.datamodel.data
        dtmp = dtmp[selCols]
        self.datamodel.SetCurrData(dtmp)
    
        print('Num cols : ' + str(len(self.datamodel.currdatacols)))

        self.PopulateSort()
        self.PopulateTable()

    def PopulateTable(self):
        if self.datamodel.data is not None:
            sortCol = self.datamodel.sortCols
            sortOrders = self.datamodel.sortOrders
            if len(sortCol)>0:
                print(sortCol)
                print(sortOrders)
                model = PandasModel(self.datamodel.currdata.sort_values(sortCol, ascending=sortOrders).head(20))
            else:
                model = PandasModel(self.datamodel.currdata.head(20))
            self.dataView.setModel(model)

    def PopulateSort(self):
        #get data column header names
        colNames = self.datamodel.currdatacols

        #add the list items to comboBox
        self.ui.comboBoxSort1.blockSignals(True)
        self.ui.comboBoxSort1.clear()
        self.ui.comboBoxSort1.blockSignals(False)
        self.ui.comboBoxSort1.addItems(colNames)

        self.ui.comboBoxSort2.blockSignals(True)
        self.ui.comboBoxSort2.clear()
        self.ui.comboBoxSort2.blockSignals(False)
        self.ui.comboBoxSort2.addItems(colNames)

    def PopulateSelect(self):
        #get data column header names
        colNames = self.datamodel.GetColumnHeaderNames()

        #add the list items to comboBox
        self.ui.comboBoxSelect.blockSignals(True)
        self.ui.comboBoxSelect.clear()
        self.ui.comboBoxSelect.blockSignals(False)
        self.ui.comboBoxSelect.addItems(colNames)


    def OnDataChanged(self):
        self.PopulateSort()
        self.PopulateSelect()
        self.PopulateTable()

    def OnCurrDataChanged(self):
        self.PopulateTable()
