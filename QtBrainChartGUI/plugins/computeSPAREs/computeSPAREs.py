from PyQt5.QtGui import *
from matplotlib.backends.backend_qt5 import FigureCanvasQT
from yapsy.IPlugin import IPlugin
from PyQt5 import QtGui, QtCore, QtWidgets, uic
import joblib
import sys, os

import seaborn as sns
import numpy as np
import pandas as pd

# Plotting with matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib as mpl
mpl.use('QT5Agg')


class PlotCanvas(FigureCanvas):
    """ A generic Plotting class that derives from FigureCanvasQTAgg
    and plots data as per different options"""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        """The constructor."""

        # a figure instance to plot on
        fig = mpl.figure.Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        #super clas
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

class computeSPAREs(QtWidgets.QWidget,IPlugin):

    #constructor
    def __init__(self):
        super(computeSPAREs,self).__init__()
        self.model = {'BrainAge': None, 'AD': None}
        root = os.path.dirname(__file__)
        self.ui = uic.loadUi(os.path.join(root, 'computeSPAREs.ui'),self)
        self.plotCanvas = PlotCanvas(self.ui.page_2)
        self.ui.verticalLayout.addWidget(self.plotCanvas)
        self.SPAREs = None
        #TODO: hook up plot functionality

        self.ui.stackedWidget.setCurrentIndex(0)


    def getUI(self):
        return self.ui


    def SetupConnections(self):
        #pass
        self.ui.load_SPARE_model_Btn.clicked.connect(lambda: self.OnLoadSPAREModel())
        self.ui.load_other_model_Btn.clicked.connect(lambda: self.OnLoadSPAREModel())
        self.ui.add_to_dataframe_Btn.clicked.connect(lambda: self.OnAddToDataFrame())
        self.ui.compute_SPARE_scores_Btn.clicked.connect(lambda: self.OnComputeSPAREs())
        self.ui.show_SPARE_scores_from_data_Btn.clicked.connect(lambda: self.OnShowSPAREs())
        self.datamodel.data_changed.connect(lambda: self.OnDataChanged())

        # Set `Show SPARE-* from data` button to visible when SPARE-* columns
        # are present in data frame
        if ('SPARE_BA' in self.datamodel.GetColumnHeaderNames() and
            'SPARE_AD' in self.datamodel.GetColumnHeaderNames()):
            self.ui.show_SPARE_scores_from_data_Btn.setEnabled(True)
        else:
            self.ui.show_SPARE_scores_from_data_Btn.setEnabled(False)

        # Allow loading of SPARE-* model only when harmonized residuals are
        # present
        if 'RES_ICV_Sex_MUSE_Volume_47' in self.datamodel.GetColumnHeaderNames():
            self.ui.load_SPARE_model_Btn.setEnabled(True)
        else:
            self.ui.load_SPARE_model_Btn.setEnabled(False)



    def OnLoadSPAREModel(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None,
            'Open SPARE-* model file',
            QtCore.QDir().homePath(),
            "Pickle files (*.pkl.gz *.pkl)")
        if fileName != "":
            self.model['BrainAge'], self.model['AD'] = joblib.load(fileName)
            self.ui.compute_SPARE_scores_Btn.setEnabled(True)
        
        self.ui.stackedWidget.setCurrentIndex(0)


    def OnComputeSPAREs(self):
        if 'RES_ICV_Sex_MUSE_Volume_47' in self.datamodel.GetColumnHeaderNames():
            self.SPAREs = pd.DataFrame.from_dict({
                'SPARE_BA': predictBrainAge(self.datamodel.data, self.model['BrainAge']),
                'SPARE_AD': predictAD(self.datamodel.data, self.model['AD'])})
            self.plotSPAREs()
            self.ui.stackedWidget.setCurrentIndex(1)
        else:
            print('No field `RES_ICV_Sex_MUSE_Volume_47` found. ' +
                  'Make sure to compute harmonized residuals first.')


    def plotSPAREs(self):
        sns.scatterplot(x='SPARE_AD', y='SPARE_BA', data=self.SPAREs,
                        ax=self.plotCanvas.axes)


    def OnAddToDataFrame(self):
        pass


    def OnShowSPAREs(self):
        self.SPAREs = pd.DataFrame.from_dict({
            'SPARE_BA': self.datamodel.data['SPARE_BA'].values,
            'SPARE_AD': self.datamodel.data['SPARE_AD'].values})
        self.plotSPAREs()
        self.ui.stackedWidget.setCurrentIndex(1)


    def OnDataChanged(self):
        # Set `Show SPARE-* from data` button to visible when SPARE-* columns
        # are present in data frame
        if ('SPARE_BA' in self.datamodel.GetColumnHeaderNames() and
            'SPARE_AD' in self.datamodel.GetColumnHeaderNames()):
            self.ui.show_SPARE_scores_from_data_Btn.setEnabled(True)
        else:
            self.ui.show_SPARE_scores_from_data_Btn.setEnabled(False)

        # Allow loading of SPARE-* model only when harmonized residuals are
        # present
        if 'RES_ICV_Sex_MUSE_Volume_47' in self.datamodel.GetColumnHeaderNames():
            self.ui.load_SPARE_model_Btn.setEnabled(True)
        else:
            self.ui.load_SPARE_model_Btn.setEnabled(False)


def predictBrainAge(data,model):
    
    idx = ~data[model['predictors'][0]].isnull()

    y_hat_test = np.zeros((np.sum(idx),))
    n_ensembles = np.zeros((np.sum(idx),))

    for i,_ in enumerate(model['scaler']):
        # Predict validation (fold) and test
        print('Fold %d' % (i))
        test = np.logical_not(data[idx]['participant_id'].isin(np.concatenate(model['train']))) | data[idx]['participant_id'].isin(model['validation'][i])
        X = data[idx].loc[test, model['predictors']].values
        X = model['scaler'][i].transform(X)
        y_hat_test[test] += (model['svm'][i].predict(X) - model['bias_ints'][i]) / model['bias_slopes'][i]
        n_ensembles[test] += 1.

    y_hat_test /= n_ensembles
    y_hat = np.full((data.shape[0],),np.nan)
    y_hat[idx] = y_hat_test

    return y_hat


def predictAD(data,model):
    
    idx = ~data[model['predictors'][0]].isnull()

    y_hat_test = np.zeros((np.sum(idx),))
    n_ensembles = np.zeros((np.sum(idx),))

    for i,_ in enumerate(model['scaler']):
        # Predict validation (fold) and test
        print('Fold %d' % (i))
        test = np.logical_not(data[idx]['participant_id'].isin(np.concatenate(model['train']))) | data[idx]['participant_id'].isin(model['validation'][i])
        X = data[idx].loc[test, model['predictors']].values
        X = model['scaler'][i].transform(X)
        y_hat_test[test] += model['svm'][i].decision_function(X)
        n_ensembles[test] += 1.

    y_hat_test /= n_ensembles
    y_hat = np.full((data.shape[0],),np.nan)
    y_hat[idx] = y_hat_test

    return y_hat
