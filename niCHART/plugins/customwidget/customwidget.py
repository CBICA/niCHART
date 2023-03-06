from PyQt5.QtGui import *
from yapsy.IPlugin import IPlugin
from PyQt5 import QtGui, QtCore, QtWidgets, uic
import sys, os
from pubsub import pub

class CustomWidget(QtWidgets.QWidget,IPlugin):

    def __init__(self):
        super(CustomWidget,self).__init__()
        self.datamodel = None
        self.SetupUi()

    def SetupConnections(self):
        self.datamodel.data_changed.connect(lambda: self.OnDataChanged())

    def SetupUi(self):
        #we manually create UI here
        self.leftPaneVLayout = QtWidgets.QVBoxLayout(self)
        self.leftPaneVLayout.setObjectName("leftPaneVLayout")

        self.dataStatisticsGroupBox = QtWidgets.QGroupBox(self)
        self.dataStatisticsGroupBox.setObjectName("dataStatisticsGroupBox")
        self.leftPaneVLayout.addWidget(self.dataStatisticsGroupBox)

        self.dataStatsGroupBoxGridLayout = QtWidgets.QGridLayout(self.dataStatisticsGroupBox)

        #Add data statistics box
        #Data File
        self.label_DataFile = QtWidgets.QLabel(self.dataStatisticsGroupBox);
        self.label_DataFile.setObjectName("label_DataFile")
        self.label_DataFile.setText("Data File:")
        self.dataStatsGroupBoxGridLayout.addWidget(self.label_DataFile, 0, 0, 1, 1);

        self.label_DataFileValue = QtWidgets.QLabel(self.dataStatisticsGroupBox)
        self.label_DataFileValue.setObjectName("label_NumParticipantsValue")
        self.dataStatsGroupBoxGridLayout.addWidget(self.label_DataFileValue,0, 1, 1, 1)

        #Harmonization Model File
        self.label_HarmonizationModelFile = QtWidgets.QLabel(self.dataStatisticsGroupBox);
        self.label_HarmonizationModelFile.setObjectName("label_HarmonizationModelFile")
        self.label_HarmonizationModelFile.setText("Harmonization Model File:")
        self.dataStatsGroupBoxGridLayout.addWidget(self.label_HarmonizationModelFile, 1, 0, 1, 1);

        self.label_HarmonizationModelFileValue = QtWidgets.QLabel(self.dataStatisticsGroupBox)
        self.label_HarmonizationModelFileValue.setObjectName("label_HarmonizationModelFileValue")
        self.dataStatsGroupBoxGridLayout.addWidget(self.label_HarmonizationModelFileValue, 1, 1, 1, 1)

        #Participants
        self.label_NumParticipants = QtWidgets.QLabel(self.dataStatisticsGroupBox);
        self.label_NumParticipants.setObjectName("label_NumParticipants")
        self.label_NumParticipants.setText("Number of Participants:")
        self.dataStatsGroupBoxGridLayout.addWidget(self.label_NumParticipants, 2, 0, 1, 1);

        self.label_NumParticipantsValue = QtWidgets.QLabel(self.dataStatisticsGroupBox)
        self.label_NumParticipantsValue.setObjectName("label_NumParticipantsValue")
        self.dataStatsGroupBoxGridLayout.addWidget(self.label_NumParticipantsValue, 2, 1, 1, 1)

        #Observations
        self.label_NumObservations = QtWidgets.QLabel(self.dataStatisticsGroupBox);
        self.label_NumObservations.setObjectName("label_NumObservations")
        self.label_NumObservations.setText("Number of Observations:")
        self.dataStatsGroupBoxGridLayout.addWidget(self.label_NumObservations, 3, 0, 1, 1);

        self.label_NumObservationsValue = QtWidgets.QLabel(self.dataStatisticsGroupBox)
        self.label_NumObservationsValue.setObjectName("label_NumObservationsValue")
        self.dataStatsGroupBoxGridLayout.addWidget(self.label_NumObservationsValue, 3, 1, 1, 1)

        #Age
        self.label_Age = QtWidgets.QLabel(self.dataStatisticsGroupBox);
        self.label_Age.setObjectName("label_Age")
        self.label_Age.setText("Age [min, max]:")
        self.dataStatsGroupBoxGridLayout.addWidget(self.label_Age, 4, 0, 1, 1);

        self.label_AgeValue = QtWidgets.QLabel(self.dataStatisticsGroupBox)
        self.label_AgeValue.setObjectName("label_AgeValue")
        self.dataStatsGroupBoxGridLayout.addWidget(self.label_AgeValue, 4, 1, 1, 1)

        #Sex[M/F]
        self.label_Sex = QtWidgets.QLabel(self.dataStatisticsGroupBox);
        self.label_Sex.setObjectName("label_Sex")
        self.label_Sex.setText("Sex [M,F]:")
        self.dataStatsGroupBoxGridLayout.addWidget(self.label_Sex, 5, 0, 1, 1);

        self.label_SexValue = QtWidgets.QLabel(self.dataStatisticsGroupBox)
        self.label_SexValue.setObjectName("label_SexValue")
        self.dataStatsGroupBoxGridLayout.addWidget(self.label_SexValue, 5, 1, 1, 1)

    def UpdateDataStatistics(self):
        #get data statistics from model
        stats = self.datamodel.GetDataStatistics()

        #add statistics values to UI
        self.label_NumParticipantsValue.setText(str(stats['numParticipants']))
        self.label_NumObservationsValue.setText(str(stats['numObservations']))
        ageVal = "[" + str(round(stats['minAge'],2)) + "," + str(round(stats['maxAge'],2)) + "]"
        self.label_AgeValue.setText(ageVal)
        sexVal = "[" + str(stats['countsPerSex']['M']) + "," + str(stats['countsPerSex']['F']) + "]"
        self.label_SexValue.setText(sexVal)

        dataFilePath = self.datamodel.GetDataFilePath()
        harmonizationModelFilePath = self.datamodel.GetHarmonizationModelFilePath()
        self.label_DataFileValue.setText(QtCore.QFileInfo(dataFilePath).fileName())
        self.label_DataFileValue.setToolTip(QtCore.QFileInfo(dataFilePath).absoluteFilePath())
        self.label_HarmonizationModelFileValue.setText(QtCore.QFileInfo(harmonizationModelFilePath).fileName())
        self.label_HarmonizationModelFileValue.setToolTip(QtCore.QFileInfo(harmonizationModelFilePath).absoluteFilePath())

    def OnDataChanged(self):
        self.UpdateDataStatistics()
