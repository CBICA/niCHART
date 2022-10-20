from PyQt5.QtGui import *
from PyQt5 import QtGui, QtCore, QtWidgets, uic
import sys, os
from NiBAx.core.baseplugin import BasePlugin

class DataCharacteristics(QtWidgets.QWidget,BasePlugin):
    priority = 0

    def __init__(self):
        super(DataCharacteristics,self).__init__()
        self.datamodel = None
        root = os.path.dirname(__file__)
        self.readAdditionalInformation(root)
        self.ui = uic.loadUi(os.path.join(root, 'datacharacteristics.ui'),self)

    def getUI(self):
        return self.ui

    def SetupConnections(self):
        self.datamodel.data_changed.connect(lambda: self.OnDataChanged())

    def UpdateDataCharacteristics(self):
        #get data statistics from model
        stats = self.datamodel.GetDataStatistics()

        #add statistics values to UI
        self.numParticipantsValue_label.setText(str(stats['numParticipants']))
        self.numObservationsValue_label.setText(str(stats['numObservations']))
        ageVal = "[" + str(round(stats['minAge'],2)) + "," + str(round(stats['maxAge'],2)) + "]"
        self.ageValue_label.setText(ageVal)
        sexVal = "[" + str(stats['countsPerSex']['M']) + "," + str(stats['countsPerSex']['F']) + "]"
        self.sexValue_label.setText(sexVal)

        dataFilePath = self.datamodel.GetDataFilePath()
        harmonizationModelFilePath = self.datamodel.GetHarmonizationModelFilePath()
        self.datafileValue_label.setText(QtCore.QFileInfo(dataFilePath).fileName())
        self.datafileValue_label.setToolTip(QtCore.QFileInfo(dataFilePath).absoluteFilePath())
        self.harmonizationfileValue_label.setText(QtCore.QFileInfo(harmonizationModelFilePath).fileName())
        self.harmonizationfileValue_label.setToolTip(QtCore.QFileInfo(harmonizationModelFilePath).absoluteFilePath())

    def OnDataChanged(self):
        self.UpdateDataCharacteristics()
