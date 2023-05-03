from PyQt5.QtGui import *
from PyQt5 import QtGui, QtCore, QtWidgets, uic
import sys, os
import neuroHarmonize as nh
from niCHART.core.baseplugin import BasePlugin

import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
from niCHART.plugins.loadsave.dataio import DataIO
from niCHART.core.plotcanvas import PlotCanvas
from niCHART.core.gui.SearchableQComboBox import SearchableQComboBox

class AgeTrends(QtWidgets.QWidget,BasePlugin):

    #constructor
    def __init__(self):
        super(AgeTrends,self).__init__()
        self.datamodel = None
        root = os.path.dirname(__file__)
        self.readAdditionalInformation(root)
        self.ui = uic.loadUi(os.path.join(root, 'agetrends.ui'),self)
        self.plotCanvas = PlotCanvas(self.ui)
        self.ui.comboBoxROI = SearchableQComboBox(self.ui)
        self.ui.comboBoxHue = SearchableQComboBox(self.ui)
        self.ui.horizontalLayout.addWidget(self.comboBoxROI)
        self.ui.horizontalLayout.addWidget(self.comboBoxHue)
        self.ui.verticalLayout.addWidget(self.plotCanvas)
        self.plotCanvas.axes = self.plotCanvas.fig.add_subplot(111)

    def getUI(self):
        return self.ui

    def SetupConnections(self):
        self.datamodel.data_changed.connect(lambda: self.OnDataChanged())
        self.datamodel.model_changed.connect(lambda: self.OnModelChanged())
        self.ui.comboBoxROI.currentIndexChanged.connect(self.UpdatePlot)
        self.ui.comboBoxHue.currentIndexChanged.connect(self.UpdatePlot)

    def OnDataChanged(self):
        self.PopulateROI()
        self.PopulateHue()

    def OnModelChanged(self):
        self.GetMUSEROIDict()
        self.PopulateROI()

    def GetMUSEROIDict(self):
        dio = DataIO()
        #also read MUSE dictionary
        MUSEDictNAMEtoID, MUSEDictIDtoNAME, MUSEDictDataFrame = dio.ReadMUSEDictionary()
        self.datamodel.SetMUSEDictionaries(MUSEDictNAMEtoID, MUSEDictIDtoNAME,MUSEDictDataFrame)

    def PopulateROI(self):
        #get data column header names
        datakeys = self.datamodel.GetColumnHeaderNames()
        #construct ROI list to populate comboBox
        roiList = (  [x for x in datakeys if x.startswith('MUSE_Volume')]
            + [x for x in datakeys if x.startswith('H_MUSE_Volume')]
            + [x for x in datakeys if x.startswith('WMLS_Volume')]
            + [x for x in datakeys if x.startswith('H_WMLS_Volume')]
            + [x for x in datakeys if x.startswith('RES_MUSE_Volume')]
            + ['SPARE_AD','SPARE_BA','Non-existing-ROI','DLICV'])

        # !!! remove ROI with no dictionary entry
        for invalid_ROI in ['WMLS_Volume_43', 'WMLS_Volume_42', 'WMLS_Volume_69',
                            'WMLS_Volume_1', 'WMLS_Volume_621', 'WMLS_Volume_622',
                            'WMLS_Volume_700' ]:
            if invalid_ROI in roiList:
                roiList.remove(invalid_ROI)

        _, MUSEDictIDtoNAME = self.datamodel.GetMUSEDictionaries()
        roiList = list(set(roiList).intersection(set(datakeys)))
        roiList.sort()
        roiList = ['(MUSE) ' + list(map(MUSEDictIDtoNAME.get, [k]))[0] if k.startswith('MUSE_') else k for k in roiList]
        roiList = ['(Harmonized MUSE) ' + list(map(MUSEDictIDtoNAME.get, [k[2:]]))[0] if k.startswith('H_MUSE_') else k for k in roiList]
        roiList = ['(WMLS) ' + list(map(MUSEDictIDtoNAME.get, [k.replace('WMLS_', 'MUSE_')]))[0] if k.startswith('WMLS_') else k for k in roiList]
        roiList = ['(Residuals MUSE) ' + list(map(MUSEDictIDtoNAME.get, [k.replace('RES_MUSE_', 'MUSE_')]))[0] if k.startswith('RES_') else k for k in roiList]

        #add the list items to comboBox
        self.ui.comboBoxROI.blockSignals(True)
        self.ui.comboBoxROI.clear()
        self.ui.comboBoxROI.blockSignals(False)
        self.ui.comboBoxROI.addItems(roiList)


    def PopulateHue(self):
        #add the list items to comboBoxHue
        datakeys = self.datamodel.GetColumnHeaderNames()
        datatypes = self.datamodel.GetColumnDataTypes()
        categoryList = ['Sex','Study','A','T','N','PIB_Status'] + [k for k,d in zip(datakeys, datatypes) if d.name=='category']
        categoryList = list(set(categoryList).intersection(set(datakeys)))
        self.ui.comboBoxROI.blockSignals(True)
        self.ui.comboBoxHue.clear()
        self.ui.comboBoxROI.blockSignals(False)
        self.ui.comboBoxHue.addItems(categoryList)

    def UpdatePlot(self):
        #get current selected combobox item
        currentROI = self.ui.comboBoxROI.currentText()
        currentHue = self.ui.comboBoxHue.currentText()

        # Translate ROI name back to ROI ID
        try:
            MUSEDictNAMEtoID, _ = self.datamodel.GetMUSEDictionaries()
            if currentROI.startswith('(MUSE)'):
                currentROI = list(map(MUSEDictNAMEtoID.get, [currentROI[7:]]))[0]

            if currentROI.startswith('(Harmonized MUSE)'):
                currentROI = 'H_' + list(map(MUSEDictNAMEtoID.get, [currentROI[18:]]))[0]

            if currentROI.startswith('(Residuals MUSE)'):
                currentROI = 'RES_' + list(map(MUSEDictNAMEtoID.get, [currentROI[17:]]))[0]

            if currentROI.startswith('(WMLS)'):
                currentROI = list(map(MUSEDictNAMEtoID.get, [currentROI[7:]]))[0].replace('MUSE_', 'WMLS_')
        except:
            currentROI = 'DLICV'
            self.ui.comboBoxROI.setCurrentText('DLICV')
            print("Could not translate combo box item. Setting to `DLICV`.")

        #create empty dictionary of plot options
        plotOptions = dict()

        #fill dictionary with options
        plotOptions['ROI'] = currentROI
        plotOptions['HUE'] = currentHue

        #Plot data
        if self.datamodel.data is not None:
            self.PlotAgeTrends(plotOptions)
        
        if (self.datamodel.harmonization_model is not None) and (self.datamodel.data is None):
            self.PlotModelTrends(plotOptions)

    def PlotAgeTrends(self,plotOptions):
        """Plot Age Trends"""
        currentROI = plotOptions['ROI']
        currentHue = plotOptions['HUE']

        if not currentHue:
            currentHue = 'Sex'

        # clear plot
        self.plotCanvas.axes.clear()

        # seaborn plot on axis
        a = sns.scatterplot(x='Age', y=currentROI,  hue=currentHue,ax=self.plotCanvas.axes, s=5,
            data=self.datamodel.GetData(currentROI,currentHue))
        self.plotCanvas.axes.yaxis.set_ticks_position('left')
        self.plotCanvas.axes.xaxis.set_ticks_position('bottom')
        sns.despine(fig=self.plotCanvas.axes.get_figure(), trim=True)
        self.plotCanvas.axes.get_figure().set_tight_layout(True)

        if (self.datamodel.harmonization_model is not None) and (currentROI in [x for x in self.datamodel.harmonization_model['ROIs']]):
            x,y,z = self.datamodel.GetNormativeRange(currentROI)
            #print('Pooled variance: %f' % (z))
            # Plot three lines as expected mean and +/- 2 times standard deviation
            sns.lineplot(x=x, y=y, ax=self.plotCanvas.axes, linestyle='-', markers=False, color='k')
            sns.lineplot(x=x, y=y+z, ax=self.plotCanvas.axes, linestyle=':', markers=False, color='k')
            sns.lineplot(x=x, y=y-z, ax=self.plotCanvas.axes, linestyle=':', markers=False, color='k')

        # Set ROI name as y-label if applicable
        _, MUSEDictIDtoNAME = self.datamodel.GetMUSEDictionaries()
        ylabel = currentROI
        #print(currentROI)
        if ylabel.startswith('MUSE_'):
            ylabel = '(MUSE) ' + list(map(MUSEDictIDtoNAME.get, [currentROI]))[0]

        if ylabel.startswith('WMLS_'):
            ylabel = '(WMLS) ' + list(map(MUSEDictIDtoNAME.get, [currentROI.replace('WMLS_', 'MUSE_')]))[0]

        if ylabel.startswith('H_MUSE_'):
            ylabel = '(Harmonized MUSE) ' + list(map(MUSEDictIDtoNAME.get, [currentROI.replace('H_', '')]))[0]

        if ylabel.startswith('RES_MUSE_'):
            ylabel = '(Residuals MUSE) ' + list(map(MUSEDictIDtoNAME.get, [currentROI.replace('RES_', '')]))[0]

        self.plotCanvas.axes.set(ylabel=ylabel)

        # refresh canvas
        self.plotCanvas.draw()

    def PlotModelTrends(self,plotOptions):
        """Plot Age Trends"""
        currentROI = plotOptions['ROI']

        # clear plot
        self.plotCanvas.axes.clear()

        if (self.datamodel.harmonization_model is not None) and (currentROI in [x for x in self.datamodel.harmonization_model['ROIs']]):
            x,y,z = self.datamodel.GetNormativeRange(currentROI,sex='M')
            u,v,w = self.datamodel.GetNormativeRange(currentROI,sex='F')
            #print('Pooled variance: %f' % (z))
            # Plot three lines as expected mean and +/- 2 times standard deviation
            sns.lineplot(x=x, y=y, ax=self.plotCanvas.axes, linestyle='-', markers=False, color='blue')
            sns.lineplot(x=x, y=y+z, ax=self.plotCanvas.axes, linestyle=':', markers=False, color='blue')
            sns.lineplot(x=x, y=y-z, ax=self.plotCanvas.axes, linestyle=':', markers=False, color='blue')
            sns.lineplot(x=u, y=v, ax=self.plotCanvas.axes, linestyle='-', markers=False, color='orange')
            sns.lineplot(x=u, y=v+w, ax=self.plotCanvas.axes, linestyle=':', markers=False, color='orange')
            sns.lineplot(x=u, y=v-w, ax=self.plotCanvas.axes, linestyle=':', markers=False, color='orange')
            custom_lines = [Line2D([0], [0], color='orange', lw=4),
                    Line2D([0], [0], color='blue', lw=4)]
            self.plotCanvas.axes.legend(custom_lines,['Female ','Male'],loc='upper left',title='Sex')


        # Set ROI name as y-label if applicable
        _, MUSEDictIDtoNAME = self.datamodel.GetMUSEDictionaries()
        ylabel = currentROI
        #print(currentROI)
        if ylabel.startswith('MUSE_'):
            ylabel = '(MUSE) ' + list(map(MUSEDictIDtoNAME.get, [currentROI]))[0]

        if ylabel.startswith('WMLS_'):
            ylabel = '(WMLS) ' + list(map(MUSEDictIDtoNAME.get, [currentROI.replace('WMLS_', 'MUSE_')]))[0]

        if ylabel.startswith('H_MUSE_'):
            ylabel = '(Harmonized MUSE) ' + list(map(MUSEDictIDtoNAME.get, [currentROI.replace('H_', '')]))[0]

        if ylabel.startswith('RES_MUSE_'):
            ylabel = '(Residuals MUSE) ' + list(map(MUSEDictIDtoNAME.get, [currentROI.replace('RES_', '')]))[0]

        self.plotCanvas.axes.set(ylabel=ylabel)

        # refresh canvas
        self.plotCanvas.draw()