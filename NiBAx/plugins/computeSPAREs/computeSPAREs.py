from PyQt5.QtGui import *
from matplotlib.backends.backend_qt5 import FigureCanvasQT
from PyQt5 import QtGui, QtCore, QtWidgets, uic
import joblib
import sys, os, time
import seaborn as sns
import numpy as np
import pandas as pd
from NiBAx.core.plotcanvas import PlotCanvas
from NiBAx.core.baseplugin import BasePlugin
from NiBAx.core.gui.SearchableQComboBox import SearchableQComboBox

class computeSPAREs(QtWidgets.QWidget,BasePlugin):

    #constructor
    def __init__(self):
        super(computeSPAREs,self).__init__()
        self.model = {'BrainAge': None, 'AD': None}
        root = os.path.dirname(__file__)
        self.readAdditionalInformation(root)
        self.ui = uic.loadUi(os.path.join(root, 'computeSPAREs.ui'),self)
        self.ui.comboBoxHue = SearchableQComboBox(self.ui)
        self.ui.horizontalLayout_3.addWidget(self.comboBoxHue)
        self.plotCanvas = PlotCanvas(self.ui.page_2)
        self.ui.verticalLayout.addWidget(self.plotCanvas)
        self.plotCanvas.axes = self.plotCanvas.fig.add_subplot(111)
        self.SPAREs = None
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.factorial_progressBar.setValue(0)

        # Initialize thread
        self.thread = QtCore.QThread()


    def getUI(self):
        return self.ui


    def SetupConnections(self):
        #pass
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


    def OnComputationDone(self, y_hat):
        self.SPAREs = y_hat
        self.ui.compute_SPARE_scores_Btn.setText('Compute SPARE-*')
        if self.SPAREs.empty:
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
            self.thread.requestInterruption()
        else:
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
            self.thread = QtCore.QThread()
            self.worker = BrainAgeWorker(self.datamodel.data, self.model)
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.worker.done.connect(self.thread.quit)
            self.worker.done.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.worker.progress.connect(self.updateProgress)
            self.worker.done.connect(lambda y_hat: self.OnComputationDone(y_hat))
            self.ui.factorial_progressBar.setRange(0, len(self.model['BrainAge']['scaler'])-1)
            self.thread.start()


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
            print(self.SPAREs[plotOptions['HUE']].value_counts())
            kws = {"s": 20}
            sns.scatterplot(x='SPARE_AD', y='SPARE_BA', data=self.SPAREs,
                        ax=self.plotCanvas.axes, linewidth=0, hue=plotOptions['HUE'],
                        facecolor=(0.5, 0.5, 0.5, 0.5), **kws) 
        else:
            kws = {"s": 20}
            sns.scatterplot(x='SPARE_AD', y='SPARE_BA', data=self.SPAREs,
                        ax=self.plotCanvas.axes, linewidth=0,
                        facecolor=(0.5, 0.5, 0.5, 0.5), legend=None)
            


        sns.despine(ax=self.plotCanvas.axes, trim=True)
        self.plotCanvas.axes.set(ylabel='SPARE-BA', xlabel='SPARE-AD')
        self.plotCanvas.axes.get_figure().set_tight_layout(True)
        self.plotCanvas.draw()


    def OnAddToDataFrame(self):
        print('Adding SPARE-* scores to data frame...')
        self.datamodel.data.loc[:,'SPARE_AD'] = self.SPAREs['SPARE_AD']
        self.datamodel.data.loc[:,'SPARE_BA'] = self.SPAREs['SPARE_BA']
        self.datamodel.data_changed.emit()
        self.OnShowSPAREs()


    def OnShowSPAREs(self):
        allHues = [self.ui.comboBoxHue.itemText(i) for i in range(self.ui.comboBoxHue.count())]

        self.SPAREs = self.datamodel.data[['SPARE_BA', 'SPARE_AD'] + allHues]
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


class BrainAgeWorker(QtCore.QObject):

    done = QtCore.pyqtSignal(pd.DataFrame)
    progress = QtCore.pyqtSignal(str, int)

    #constructor
    def __init__(self, data, model):
        super(BrainAgeWorker, self).__init__()
        self.data = data
        self.model = model

    def run(self):
        y_hat = pd.DataFrame.from_dict({'SPARE_BA': np.full((self.data.shape[0],),np.nan),
                                       'SPARE_AD': np.full((self.data.shape[0],),np.nan)})

        # SPARE-BA
        idx = ~self.data[self.model['BrainAge']['predictors'][0]].isnull()

        y_hat_test = np.zeros((np.sum(idx),))
        n_ensembles = np.zeros((np.sum(idx),))

        for i,_ in enumerate(self.model['BrainAge']['scaler']):
            # Predict validation (fold) and test
            self.progress.emit('Computing SPARE-BA | Task 1 of 2', i)
            if QtCore.QThread.currentThread().isInterruptionRequested():
                self.progress.emit('Cancelled.', 0)
                self.done.emit(pd.DataFrame())
                return
            test = np.logical_not(self.data[idx]['participant_id'].isin(np.concatenate(self.model['BrainAge']['train']))) | self.data[idx]['participant_id'].isin(self.model['BrainAge']['validation'][i])
            X = self.data[idx].loc[test, self.model['BrainAge']['predictors']].values
            X = self.model['BrainAge']['scaler'][i].transform(X)
            y_hat_test[test] += (self.model['BrainAge']['svm'][i].predict(X) - self.model['BrainAge']['bias_ints'][i]) / self.model['BrainAge']['bias_slopes'][i]
            n_ensembles[test] += 1.

        y_hat_test /= n_ensembles
        y_hat.loc[idx, 'SPARE_BA'] = y_hat_test

        idx = ~self.data[self.model['AD']['predictors'][0]].isnull()

        y_hat_test = np.zeros((np.sum(idx),))
        n_ensembles = np.zeros((np.sum(idx),))

        for i,_ in enumerate(self.model['AD']['scaler']):
            # Predict validation (fold) and test
            self.progress.emit('Computing SPARE-AD | Task 2 of 2', i)
            if QtCore.QThread.currentThread().isInterruptionRequested():
                self.progress.emit('Cancelled.', 0)
                # Emit the result
                self.done.emit(pd.DataFrame())
                return
            test = np.logical_not(self.data[idx]['participant_id'].isin(np.concatenate(self.model['AD']['train']))) | self.data[idx]['participant_id'].isin(self.model['AD']['validation'][i])
            X = self.data[idx].loc[test, self.model['AD']['predictors']].values
            X = self.model['AD']['scaler'][i].transform(X)
            y_hat_test[test] += self.model['AD']['svm'][i].decision_function(X)
            n_ensembles[test] += 1. 

        y_hat_test /= n_ensembles
        y_hat.loc[idx, 'SPARE_AD'] = y_hat_test

        self.progress.emit('All done.', i)

        # Emit the result
        self.done.emit(y_hat)
