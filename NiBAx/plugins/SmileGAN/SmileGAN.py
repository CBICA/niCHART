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
from SmileGAN.Smile_GAN_clustering import clustering_result

class computeSmileGANs(QtWidgets.QWidget,BasePlugin):

    #constructor
    def __init__(self):
        super(computeSmileGANs,self).__init__()
        self.model = []
        root = os.path.dirname(__file__)
        self.readAdditionalInformation(root)
        self.ui = uic.loadUi(os.path.join(root, 'SmileGAN.ui'),self)
        self.ui.comboBoxHue = SearchableQComboBox(self.ui)
        self.ui.horizontalLayout_3.addWidget(self.comboBoxHue)
        self.plotCanvas = PlotCanvas(self.ui.page_2)
        self.ui.verticalLayout.addWidget(self.plotCanvas)
        self.plotCanvas.axes = self.plotCanvas.fig.add_subplot(111)
        self.SmileGANpatterns = None
        self.ui.stackedWidget.setCurrentIndex(0)

        # Initialize thread
        self.thread = QtCore.QThread()


    def getUI(self):
        return self.ui


    def SetupConnections(self):
        #pass
        self.ui.load_SmileGAN_model_Btn.clicked.connect(lambda: self.OnLoadSmileGANModel())
        self.ui.load_other_model_Btn.clicked.connect(lambda: self.OnLoadSmileGANModel())
        self.ui.add_to_dataframe_Btn.clicked.connect(lambda: self.OnAddToDataFrame())
        self.ui.compute_SmileGAN_Btn.clicked.connect(lambda check: self.OnComputePatterns(check))
        self.ui.show_SmileGAN_prob_from_data_Btn.clicked.connect(lambda: self.OnShowPatterns())
        self.datamodel.data_changed.connect(lambda: self.OnDataChanged())
        self.ui.comboBoxHue.currentIndexChanged.connect(self.plotPattern)

        self.ui.add_to_dataframe_Btn.setStyleSheet("background-color: green; color: white")
        # Set `Show SmileGAN patterns from data` button to visible when SmileGAN_Pattern column
        # are present in data frame
        if ('SmileGAN_Pattern' in self.datamodel.GetColumnHeaderNames()):
            self.ui.show_SmileGAN_prob_from_data_Btn.setStyleSheet("background-color: rgb(230,230,255)")
            self.ui.show_SmileGAN_prob_from_data_Btn.setEnabled(True)
            self.ui.show_SmileGAN_prob_from_data_Btn.setToolTip('The data frame has variables `SmileGAN patterns` so these can be plotted.')
        else:
            self.ui.show_SmileGAN_prob_from_data_Btn.setEnabled(False)

        # Allow loading of SmileGAN-* model always, even when residuals are not
        # calculated yet
        self.ui.load_SmileGAN_model_Btn.setEnabled(True)


    def OnLoadSmileGANModel(self):
        fileNames, _ = QtWidgets.QFileDialog.getOpenFileNames(None,
            'Open SmileGAN model file',
            QtCore.QDir().homePath(),
            "")
        if len(fileNames) > 0:
            self.model = fileNames
            self.ui.compute_SmileGAN_Btn.setEnabled(True)
            model_info = 'File:'
            for file in fileNames:
                model_info += file + '\n'
            self.ui.SmileGAN_model_info.setText(model_info)
        else:
            return
        
        self.ui.stackedWidget.setCurrentIndex(0)

        if 'RES_ICV_Sex_MUSE_Volume_47' in self.datamodel.GetColumnHeaderNames():
            self.ui.compute_SmileGAN_Btn.setStyleSheet("QPushButton"
                             "{"
                             "background-color : rgb(230,255,230);"
                             "}"
                             "QPushButton::checked"
                             "{"
                             "background-color : rgb(255,230,230);"
                             "border: none;"
                             "}"
                             )
            self.ui.compute_SmileGAN_Btn.setEnabled(True)
            self.ui.compute_SmileGAN_Btn.setChecked(False)
            self.ui.compute_SmileGAN_Btn.setToolTip('Model loaded and `RES_ICV_Sex_MUSE_Volmue_*` available so the MUSE volumes can be harmonized.')
        else:
            self.ui.compute_SmileGAN_Btn.setStyleSheet("background-color: rgb(255,230,230)")
            self.ui.compute_SmileGAN_Btn.setEnabled(False)
            self.ui.compute_SmileGAN_Btn.setToolTip('Model loaded but `RES_ICV_Sex_MUSE_Volmue_*` not available so the MUSE volumes can not be harmonized.')


            print('No field `RES_ICV_Sex_MUSE_Volume_47` found. ' +
                  'Make sure to compute and add harmonized residuals first.')

    def OnComputationDone(self, p):
        self.SmileGANpatterns = p
        self.ui.compute_SmileGAN_Btn.setText('Compute SmileGAN Patterns-*')
        if self.SmileGANpatterns.empty:
            return
        self.ui.compute_SmileGAN_Btn.setChecked(False)
        self.ui.stackedWidget.setCurrentIndex(1)
        self.ui.comboBoxHue.setVisible(False)
        self.plotPattern()

        # Activate buttons
        self.ui.compute_SmileGAN_Btn.setEnabled(False)
        if ('SmileGAN_Pattern' in self.datamodel.GetColumnHeaderNames()):
            self.ui.show_SmileGAN_prob_from_data_Btn.setEnabled(True)
        else:
            self.ui.show_SmileGAN_prob_from_data_Btn.setEnabled(False)
        self.ui.load_SmileGAN_model_Btn.setEnabled(True)
        


    def OnComputePatterns(self, checked):
        # Setup tasks for long running jobs
        # Using this example: https://realpython.com/python-pyqt-qthread/
        # Disable buttons
        if checked is not True:
            self.thread.requestInterruption()
        else:
            self.ui.compute_SmileGAN_Btn.setStyleSheet("QPushButton"
                             "{"
                             "background-color : rgb(230,255,230);"
                             "}"
                             "QPushButton::checked"
                             "{"
                             "background-color : rgb(255,230,230);"
                             "}"
                             )
            self.ui.compute_SmileGAN_Btn.setText('Cancel computation')
            self.ui.show_SmileGAN_prob_from_data_Btn.setEnabled(False)
            self.ui.load_SmileGAN_model_Btn.setEnabled(False)
            self.thread = QtCore.QThread()
            self.worker = PatternWorker(self.datamodel.data, self.model)
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.worker.done.connect(self.thread.quit)
            self.worker.done.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.worker.done.connect(lambda p: self.OnComputationDone(p))
            self.thread.start()


    def plotPattern(self):
        # Plot data
        if self.ui.stackedWidget.currentIndex() == 0:
            return
        self.plotCanvas.axes.clear()

        sns.countplot(x='Pattern', data=self.SmileGANpatterns,
                        ax=self.plotCanvas.axes) 

        sns.despine(ax=self.plotCanvas.axes, trim=True)
        self.plotCanvas.axes.set(ylabel='Count', xlabel='Patterns')
        self.plotCanvas.axes.get_figure().set_tight_layout(True)
        self.plotCanvas.draw()


    def OnAddToDataFrame(self):
        print('Adding SmileGAN patterns to data frame...')
        for col in self.SmileGANpatterns.columns:
            self.datamodel.data.loc[:,'SmileGAN_'+col] = self.SmileGANpatterns[col]
        self.datamodel.data_changed.emit()
        self.OnShowPatterns()


    def OnShowPatterns(self):
        self.ui.stackedWidget.setCurrentIndex(1)
        self.plotPattern()


    def OnDataChanged(self):
        # Set `Show SmileGAN patterns from data` button to visible when SmileGAN_Pattern column
        # are present in data frame
        self.ui.stackedWidget.setCurrentIndex(0)
        if ('SmileGAN_Pattern' in self.datamodel.GetColumnHeaderNames()):
            self.ui.show_SmileGAN_prob_from_data_Btn.setEnabled(True)
            self.ui.show_SmileGAN_prob_from_data_Btn.setStyleSheet("background-color: rgb(230,230,255)")
        else:
            self.ui.show_SmileGAN_prob_from_data_Btn.setEnabled(False)


class PatternWorker(QtCore.QObject):

    done = QtCore.pyqtSignal(pd.DataFrame)
    progress = QtCore.pyqtSignal(str, int)

    #constructor
    def __init__(self, data, model_list):
        super(PatternWorker, self).__init__()
        self.data = data
        self.model = model_list

    def run(self):
        train_data = self.data[['participant_id']+[ name for name in self.data.columns if ('H_MUSE_Volume' in name and int(name[14:])<300)] ]
        covariate = self.data[['participant_id','Age','Sex']]
        covariate['Sex'] = covariate['Sex'].map({'M':1,'F':0})
        train_data['diagnosis'] = 1
        covariate['diagnosis'] = 1
        cluster_label, cluster_prob, _, _ = clustering_result(self.model, 'highest_matching_clustering', train_data, covariate)
        p = pd.DataFrame(data = cluster_prob, columns = ['P'+str(_) for _ in range(1,cluster_prob.shape[1]+1)])
        p['Pattern'] = cluster_label
        
        # Emit the result
        self.done.emit(p)
