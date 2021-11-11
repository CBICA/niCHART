from PyQt5.QtGui import *
from yapsy.IPlugin import IPlugin
from PyQt5 import QtGui, QtCore, QtWidgets, uic
import sys, os

class DataCharacteristics(IPlugin):
    priority = 0

    def init(self, dataModel=None):
        self.datamodel = dataModel
        root = os.path.dirname(sys.argv[0])
        self.ui = uic.loadUi(os.path.join(root, 'plugins', 'DataCharacteristics', 'datacharacteristics.ui'))

    def getUI(self):
        return self.ui
