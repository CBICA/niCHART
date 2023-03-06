from PyQt5.QtGui import *
from matplotlib.backends.backend_qt5 import FigureCanvasQT
from PyQt5 import QtGui, QtCore, QtWidgets, uic
import joblib
import sys, os, time
import seaborn as sns
import numpy as np
import pandas as pd
from niCHART.core.plotcanvas import PlotCanvas
from niCHART.core.baseplugin import BasePlugin
from niCHART.core.gui.SearchableQComboBox import SearchableQComboBox
from niCHART.plugins.sparesplugin.spares import SPARE

class SparePlugin(QtWidgets.QWidget,BasePlugin):

    #constructor
    def __init__(self):
        super(SparePlugin,self).__init__()
        self.model = {'BrainAge': None, 'AD': None}
        root = os.path.dirname(__file__)
        self.readAdditionalInformation(root)
        self.ui = uic.loadUi(os.path.join(root, 'sparesplugin.ui'),self)
        self.ui.comboBoxHue = SearchableQComboBox(self.ui)
        self.ui.horizontalLayout_3.addWidget(self.comboBoxHue)
        self.plotCanvas = PlotCanvas(self.ui.page_2)
        self.ui.verticalLayout.addWidget(self.plotCanvas)
        self.plotCanvas.axes = self.plotCanvas.fig.add_subplot(111)
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.factorial_progressBar.setValue(0)
        self.spare_compute_instance = None

    def getUI(self):
        return self.ui


    def SetupConnections(self):
        self.ui.load_SPARE_model_Btn.clicked.connect(lambda: self.OnLoadSPAREModel())
        self.ui.load_other_model_Btn.clicked.connect(lambda: self.OnLoadSPAREModel())
        self.ui.add_to_dataframe_Btn.clicked.connect(lambda: self.OnAddToDataFrame())
        self.ui.compute_SPARE_scores_Btn.clicked.connect(lambda check: self.OnComputeSPAREs(check))
        self.ui.show_SPARE_scores_from_data_Btn.clicked.connect(lambda: self.OnShowSPAREs())
        self.datamodel.data_changed.connect(lambda: self.OnDataChanged())
        self.ui.comboBoxHue.currentIndexChanged.connect(self.plotSPAREs)

        self.ui.add_to_dataframe_Btn.setStyleSheet("background-color: green; color: white")
        # Set `Show SPARE-* from data` button to visible when SPARE-* columns
        # are present in data frame
        if ('SPARE_BA' in self.datamodel.GetColumnHeaderNames() and
            'SPARE_AD' in self.datamodel.GetColumnHeaderNames()):
            self.ui.show_SPARE_scores_from_data_Btn.setStyleSheet("background-color: rgb(230,230,255)")
            self.ui.show_SPARE_scores_from_data_Btn.setEnabled(True)
            self.ui.show_SPARE_scores_from_data_Btn.setToolTip('The data frame has variables `SPARE_AD` and `SPARE_BA` so these can be plotted.')
        else:
            self.ui.show_SPARE_scores_from_data_Btn.setEnabled(False)

        # Allow loading of SPARE-* model always, even when residuals are not
        # calculated yet
        self.ui.load_SPARE_model_Btn.setEnabled(True)


    def updateProgress(self, txt, vl):
        self.ui.SPARE_computation_info.setText(txt)
        self.ui.factorial_progressBar.setValue(vl)


    def OnLoadSPAREModel(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None,
            'Open SPARE-* model file',
            QtCore.QDir().homePath(),
            "Pickle files (*.pkl.gz *.pkl)")
        if fileName != "":
            self.model['BrainAge'], self.model['AD'] = joblib.load(fileName)
            self.ui.compute_SPARE_scores_Btn.setEnabled(True)
            self.ui.SPARE_model_info.setText('File: %s' % (fileName))
        else:
            return
        
        self.ui.stackedWidget.setCurrentIndex(0)

        if 'RES_ICV_Sex_MUSE_Volume_47' in self.datamodel.GetColumnHeaderNames():
            self.ui.compute_SPARE_scores_Btn.setStyleSheet("QPushButton"
                             "{"
                             "background-color : rgb(230,255,230);"
                             "}"
                             "QPushButton::checked"
                             "{"
                             "background-color : rgb(255,230,230);"
                             "border: none;"
                             "}"
                             )
            self.ui.compute_SPARE_scores_Btn.setEnabled(True)
            self.ui.compute_SPARE_scores_Btn.setChecked(False)
            self.ui.compute_SPARE_scores_Btn.setToolTip('Model loaded and `RES_ICV_Sex_MUSE_Volmue_*` available so the MUSE volumes can be harmonized.')
        else:
            self.ui.compute_SPARE_scores_Btn.setStyleSheet("background-color: rgb(255,230,230)")
            self.ui.compute_SPARE_scores_Btn.setEnabled(False)
            self.ui.compute_SPARE_scores_Btn.setToolTip('Model loaded but `RES_ICV_Sex_MUSE_Volmue_*` not available so the MUSE volumes can not be harmonized.')


            print('No field `RES_ICV_Sex_MUSE_Volume_47` found. ' +
                  'Make sure to compute and add harmonized residuals first.')


    def OnComputationDone(self):
        spares = self.spare_compute_instance.SPAREs
        self.ui.compute_SPARE_scores_Btn.setText('Compute SPARE-*')
        if spares.empty:
            return
        self.ui.compute_SPARE_scores_Btn.setChecked(False)
        self.ui.stackedWidget.setCurrentIndex(1)
        self.ui.comboBoxHue.setVisible(False)
        self.plotSPAREs(False)

        # Activate buttons
        self.ui.compute_SPARE_scores_Btn.setEnabled(False)
        if ('SPARE_BA' in self.datamodel.GetColumnHeaderNames() and
            'SPARE_AD' in self.datamodel.GetColumnHeaderNames()):
            self.ui.show_SPARE_scores_from_data_Btn.setEnabled(True)
            #self.ui.show_SPARE_scores_from_data_Btn.setStyleSheet("background-color: rgb(230,230,255)")
        else:
            self.ui.show_SPARE_scores_from_data_Btn.setEnabled(False)
        self.ui.load_SPARE_model_Btn.setEnabled(True)
        


    def OnComputeSPAREs(self, checked):
        # Setup tasks for long running jobs
        # Using this example: https://realpython.com/python-pyqt-qthread/

        # Disable buttons
        if checked is not True:
            self.spare_compute_instance.InterruptComputation()
            self.ui.compute_SPARE_scores_Btn.setStyleSheet("QPushButton"
                             "{"
                             "background-color : rgb(230,255,230);"
                             "}"
                             "QPushButton::checked"
                             "{"
                             "background-color : rgb(255,230,230);"
                             "border: none;"
                             "}"
                             )
            self.ui.compute_SPARE_scores_Btn.setText('Compute SPARE-*')
            self.ui.show_SPARE_scores_from_data_Btn.setEnabled(False)
            self.ui.load_SPARE_model_Btn.setEnabled(False)
        else:
            self.spare_compute_instance = SPARE(self.datamodel,self.model)
            self.ui.compute_SPARE_scores_Btn.setStyleSheet("QPushButton"
                             "{"
                             "background-color : rgb(230,255,230);"
                             "}"
                             "QPushButton::checked"
                             "{"
                             "background-color : rgb(255,230,230);"
                             "}"
                             )
            self.ui.compute_SPARE_scores_Btn.setText('Cancel computation')
            self.ui.show_SPARE_scores_from_data_Btn.setEnabled(False)
            self.ui.load_SPARE_model_Btn.setEnabled(False)
            self.ui.factorial_progressBar.setRange(0, len(self.model['BrainAge']['scaler'])-1)
            self.spare_compute_instance.DoSPAREsComputation(True)
            self.spare_compute_instance.sendprogress.connect(self.updateProgress)
            self.spare_compute_instance.done.connect(self.OnComputationDone)


    def PopulateHue(self):
        #add the list items to comboBoxHue
        datakeys = self.datamodel.GetColumnHeaderNames()
        datatypes = self.datamodel.GetColumnDataTypes()
        categoryList = ['Sex','Study','A','T','N','PIB_Status'] + [k for k,d in zip(datakeys, datatypes) if d.name=='category']
        categoryList = list(set(categoryList).intersection(set(datakeys)))
        self.ui.comboBoxHue.clear()
        self.ui.comboBoxHue.addItems(categoryList)


    def plotSPAREs(self, useExistingSPAREs=True):
        # Plot data
        if self.ui.stackedWidget.currentIndex() == 0:
            return
        self.plotCanvas.axes.clear()
        plotOptions = {'HUE': self.ui.comboBoxHue.currentText()}

        if useExistingSPAREs:
            #print(self.SPAREs[plotOptions['HUE']].value_counts())
            print(self.spare_compute_instance.SPAREs[plotOptions['HUE']].value_counts())
            kws = {"s": 20}
            sns.scatterplot(x='SPARE_AD', y='SPARE_BA', data=self.spare_compute_instance.SPAREs,
                        ax=self.plotCanvas.axes, linewidth=0, hue=plotOptions['HUE'],
                        facecolor=(0.5, 0.5, 0.5, 0.5), **kws) 
        else:
            kws = {"s": 20}
            sns.scatterplot(x='SPARE_AD', y='SPARE_BA', data=self.spare_compute_instance.SPAREs,
                        ax=self.plotCanvas.axes, linewidth=0,
                        facecolor=(0.5, 0.5, 0.5, 0.5), legend=None)
            


        sns.despine(ax=self.plotCanvas.axes, trim=True)
        self.plotCanvas.axes.set(ylabel='SPARE-BA', xlabel='SPARE-AD')
        self.plotCanvas.axes.get_figure().set_tight_layout(True)
        self.plotCanvas.draw()


    def OnAddToDataFrame(self):
        self.datamodel.AddSparesToDataModel(self.spare_compute_instance.SPAREs)
        self.OnShowSPAREs()


    def OnShowSPAREs(self):
        allHues = [self.ui.comboBoxHue.itemText(i) for i in range(self.ui.comboBoxHue.count())]
        self.spare_compute_instance.SPAREs = self.datamodel.data[['SPARE_BA', 'SPARE_AD'] + allHues]
        self.ui.stackedWidget.setCurrentIndex(1)
        self.ui.comboBoxHue.setVisible(True)
        self.plotSPAREs()


    def OnDataChanged(self):
        # Set `Show SPARE-* from data` button to visible when SPARE-* columns
        # are present in data frame
        self.ui.stackedWidget.setCurrentIndex(0)
        if ('SPARE_BA' in self.datamodel.GetColumnHeaderNames() and
            'SPARE_AD' in self.datamodel.GetColumnHeaderNames()):
            self.ui.show_SPARE_scores_from_data_Btn.setEnabled(True)
            self.ui.show_SPARE_scores_from_data_Btn.setStyleSheet("background-color: rgb(230,230,255)")
        else:
            self.ui.show_SPARE_scores_from_data_Btn.setEnabled(False)
        
        self.PopulateHue()

