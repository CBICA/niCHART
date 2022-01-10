from PyQt5.QtGui import *
from matplotlib.backends.backend_qt5 import FigureCanvasQT
from PyQt5 import QtGui, QtCore, QtWidgets, uic
import joblib
import sys, os, time
import seaborn as sns
import scipy as sp
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from QtBrainChartGUI.core.plotcanvas import PlotCanvas
from QtBrainChartGUI.core.baseplugin import BasePlugin

class MUSEQC(QtWidgets.QWidget,BasePlugin):

    #constructor
    def __init__(self):
        super(MUSEQC, self).__init__()
        root = os.path.dirname(__file__)
        self.readAdditionalInformation(root)
        self.ui = uic.loadUi(os.path.join(root, 'MUSEQC.ui'),self)
        self.plotCanvas = PlotCanvas(self.ui.page_2)
        self.ui.verticalLayout.addWidget(self.plotCanvas)
        self.plotCanvas.axes = self.plotCanvas.fig.add_subplot(111)
        self.ui.stackedWidget.setCurrentIndex(0)


    def getUI(self):
        return self.ui


    def SetupConnections(self):
        self.ui.doQC_Btn.clicked.connect(lambda: self.OnDoQC())
        self.datamodel.data_changed.connect(lambda: self.OnDataChanged())


    def OnDoQC(self):
        MUSEDict = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'BrainChart', 'MUSE_ROI_Dictionary.csv')
        MUSEDict = pd.read_csv(MUSEDict)

        ROIs = list(MUSEDict.loc[MUSEDict['ROI_LEVEL']=='SINGLE', 'ROI_COL'])
        ROIs.remove('MUSE_Volume_46')  # CSF
        ROIs.remove('MUSE_Volume_63')  # Right vessel
        ROIs.remove('MUSE_Volume_64')  # Left vessel
        pca = PCA(n_components=3)
        pca.fit(self.datamodel.data[ROIs].values)
        vals_pca = pca.transform(self.datamodel.data[ROIs].values)
        mean_vals_pca = np.mean(vals_pca, axis=0)
        VI = sp.linalg.inv(np.cov(vals_pca.T))
        md = vals_pca - mean_vals_pca
        md = np.abs(np.sum(md * np.dot(VI, md.T).T, axis=1))
        order = md.argsort()
        print('Ten worst cases in terms of Mahalanobis distance')
        print(self.datamodel.data.loc[order[-10:]])


    def plotQC(self):
        # Plot data
        sns.scatterplot(x='SPARE_AD', y='SPARE_BA', data=self.SPAREs,
                        ax=self.plotCanvas.axes, linewidth=0,
                        facecolor=(0.5, 0.5, 0.5, 0.5), size=1, legend=None)
        sns.despine(ax=self.plotCanvas.axes, trim=True)
        self.plotCanvas.axes.set(ylabel='SPARE-BA', xlabel='SPARE-AD')
        self.plotCanvas.axes.get_figure().set_tight_layout(True)


    def OnDataChanged(self):
        pass

