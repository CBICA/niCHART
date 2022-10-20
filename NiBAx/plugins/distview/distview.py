from PyQt5.QtGui import *
from PyQt5 import QtGui, QtCore, QtWidgets, uic
from PyQt5.QtWidgets import QMdiArea, QMdiSubWindow, QTextEdit
import sys, os
import pandas as pd
from NiBAx.core.dataio import DataIO
# import dtale
from NiBAx.core.baseplugin import BasePlugin
from NiBAx.core import iStagingLogger
from NiBAx.core.gui.SearchableQComboBox import SearchableQComboBox
from NiBAx.core.gui.CheckableQComboBox import CheckableQComboBox
from NiBAx.core.plotcanvas import PlotCanvas
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.cm import get_cmap
from matplotlib.lines import Line2D

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

class DistView(QtWidgets.QWidget,BasePlugin):

    def __init__(self):
        super(DistView,self).__init__()
        self.datamodel = None
        root = os.path.dirname(__file__)
        self.readAdditionalInformation(root)
        self.ui = uic.loadUi(os.path.join(root, 'distview.ui'),self)
        
        self.mdi = self.findChild(QMdiArea, 'mdiArea')       
        
        self.ui.comboBoxXVar = SearchableQComboBox(self.ui)
        self.ui.vlBAA.addWidget(self.ui.comboBoxXVar)

        self.ui.comboBoxFilterVar = SearchableQComboBox(self.ui)
        self.ui.vlBAC.addWidget(self.ui.comboBoxFilterVar)

        self.ui.comboBoxFilterVar2 = CheckableQComboBox(self.ui)
        self.ui.vlBAD.addWidget(self.ui.comboBoxFilterVar2)

        self.ui.comboBoxHueVar = SearchableQComboBox(self.ui)
        self.ui.vlBAE.addWidget(self.ui.comboBoxHueVar)

        self.ui.comboBoxHueVar2 = CheckableQComboBox(self.ui)
        self.ui.vlBAF.addWidget(self.ui.comboBoxHueVar2)

        self.ui.wB.setMaximumWidth(300)

        #self.PopulateVars()
        #self.ui.vlB.addStretch()
        #self.ui.vlBAB.addStretch()


    def SetupConnections(self):
        print('todo')
        self.ui.plotBtn.clicked.connect(lambda: self.OnPlotBtnClicked())
        self.datamodel.data_changed.connect(lambda: self.OnDataChanged())
        self.datamodel.currdata_changed.connect(lambda: self.OnCurrDataChanged())
        self.ui.comboBoxHueVar.currentIndexChanged.connect(lambda: self.OnHueIndexChanged())
        self.ui.comboBoxFilterVar.currentIndexChanged.connect(lambda: self.OnFilterIndexChanged())

    def OnFilterIndexChanged(self):
        selFilter = self.ui.comboBoxFilterVar.currentText()
        selFilterVals = self.datamodel.data[selFilter].unique()
        
        if len(selFilterVals) < 20:
            self.ui.comboBoxFilterVar2.blockSignals(True)
            self.ui.comboBoxFilterVar2.clear()
            self.ui.comboBoxFilterVar2.blockSignals(False)
            self.ui.comboBoxFilterVar2.addItems(selFilterVals)
        else:
            print('Too many unique values for selection, skip : ' +  selFilter + ' ' + str(len(selFilterVals)))

    def OnHueIndexChanged(self):
        selHue = self.ui.comboBoxHueVar.currentText()
        selHueVals = self.datamodel.data[selHue].unique()
        
        if len(selHueVals) < 20:
            self.ui.comboBoxHueVar2.blockSignals(True)
            self.ui.comboBoxHueVar2.clear()
            self.ui.comboBoxHueVar2.blockSignals(False)
            self.ui.comboBoxHueVar2.addItems(selHueVals)
        else:
            print('Too many unique values for selection, skip : ' + str(len(selHueVals)))


    def OnPlotBtnClicked(self):
        xVar = self.ui.comboBoxXVar.currentText()
        
        hueVar = self.ui.comboBoxHueVar.currentText()
        hueVarVals = self.ui.comboBoxHueVar2.listCheckedItems()
        
        filterVar = self.ui.comboBoxFilterVar.currentText()
        filterVarVals = self.ui.comboBoxFilterVar2.listCheckedItems()

        self.plotCanvas = PlotCanvas(self.ui)
        self.plotCanvas.axes = self.plotCanvas.fig.add_subplot(111)

        sub = QMdiSubWindow()
        sub.setWidget(self.plotCanvas)
        self.mdi.addSubWindow(sub)        
        self.PlotData(xVar, filterVar, filterVarVals, hueVar, hueVarVals)
        sub.show()
        self.mdi.tileSubWindows()

    def PopulateVars(self):
        #get data column header names
        colNames = self.datamodel.currdatacols
        
        #add the list items to comboBox
        for cbox in [self.ui.comboBoxXVar, self.ui.comboBoxHueVar, self.ui.comboBoxFilterVar]:
            cbox.blockSignals(True)
            cbox.clear()
            cbox.blockSignals(False)
            cbox.addItems(colNames)

        ##add the list items to comboBox
        ##self.ui.comboBoxXVar.blockSignals(True)
        ##self.ui.comboBoxXVar.clear()
        ##self.ui.comboBoxXVar.blockSignals(False)
        #print('OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO')
        #print(self.datamodel)
        ##print(self.datamodel.currdatacols)
        ##self.ui.comboBoxXVar.addItems(colNames)

    def PopulateSelect(self):
        #get data column header names
        colNames = self.datamodel.GetColumnHeaderNames()

        #add the list items to comboBox
        self.ui.comboBoxSelect.blockSignals(True)
        self.ui.comboBoxSelect.clear()
        self.ui.comboBoxSelect.blockSignals(False)
        self.ui.comboBoxSelect.addItems(colNames)


    def OnDataChanged(self):
        self.PopulateVars()
        #self.PopulateSelect()
        #self.PopulateTable()

    def OnCurrDataChanged(self):
        self.PopulateVars()
        
    def PlotData(self, xVar, filterVar, filterVarVals, hueVar, hueVarVals):

        # clear plot
        self.plotCanvas.axes.clear()

        ## Get data
        data = self.datamodel.GetDataSelCols([xVar, filterVar, hueVar])

        ## Filter data
        if len(filterVarVals)>0:
            data = data[data[filterVar].isin(filterVarVals)]

        ## Get hue values
        if len(hueVarVals)>0:
            data = data[data[hueVar].isin(hueVarVals)]
        
        # seaborn plot on axis
        #a = sns.scatterplot(x=xVar, y=yVar, hue=hueVar, ax=self.plotCanvas.axes, s=5, data=data)

        #sns.displot(data=data, x=xVar, hue=hueVar, kind='kde', ax=self.plotCanvas.axes)
        sns.kdeplot(data=data, x=xVar, hue=hueVar, ax=self.plotCanvas.axes)
        #self.plotCanvas.axes.legend(handles=b)

        #self.plotCanvas.axes.yaxis.set_ticks_position('left')
        #self.plotCanvas.axes.xaxis.set_ticks_position('bottom')

        sns.despine(fig=self.plotCanvas.axes.get_figure(), trim=True)
        self.plotCanvas.axes.get_figure().set_tight_layout(True)
        
        self.plotCanvas.axes.set(xlabel=xVar)
        #self.plotCanvas.axes.set(ylabel=yVar)

        # refresh canvas
        self.plotCanvas.draw()

