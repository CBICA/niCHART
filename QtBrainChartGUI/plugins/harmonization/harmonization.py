from PyQt5.QtGui import *
from yapsy.IPlugin import IPlugin
from PyQt5 import QtGui, QtCore, QtWidgets, uic
import sys, os

class Harmonization(QtWidgets.QWidget,IPlugin):

    #constructor
    def __init__(self):
        super(Harmonization,self).__init__()
        self.datamodel = None
        root = os.path.dirname(sys.argv[0])
        self.ui = uic.loadUi(os.path.join(root, 'plugins', 'Harmonization', 'harmonization.ui'),self)
        #TODO: hook up plot functionality

    def getUI(self):
        return self.ui

    def SetupConnections(self):
        #pass
        self.ui.load_harmonization_model_Btn.clicked.connect(lambda: self.OnLoadHarmonizationModelBtnClicked())
        self.datamodel.data_changed.connect(lambda: self.OnDataChanged())


    def OnLoadHarmonizationModelBtnClicked(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(None,
        'Open harmonization model file',
        QtCore.QDir().homePath(),
        "Pickle files (*.pkl.gz)")

        #read input data
        #dio = DataIO()
        #d = dio.ReadPickleFile(filename[0])

        #set data in model
        #self.datamodel.SetData(d)

    def OnLoadOtherModel(self):
        pass

    def OnAddToDataFrame(self):
        pass

    def OnDataChanged(self):
        pass
