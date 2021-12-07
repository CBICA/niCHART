# This Python file uses the following encoding: utf-8
"""
contact: software@cbica.upenn.edu
Copyright (c) 2018 University of Pennsylvania. All rights reserved.
Use of this source code is governed by license located in license file: https://github.com/CBICA/BrainChart/blob/main/LICENSE
"""
from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import seaborn as sns
import random
import pandas as pd
import os

class PlotCanvas(FigureCanvas):
    """ A generic Plotting class that derives from FigureCanvasQTAgg
    and plots data as per different options"""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        """The constructor."""

        # a figure instance to plot on
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        #super clas
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def Plot(self,datamodel,plotOptions):
        """call appropriate plotting functionality as per plot options"""
        if(str(plotOptions['VIEW']) == 'AgeTrend'):
            self.PlotAgeTrends(datamodel,plotOptions)
        elif(str(plotOptions['VIEW']) == 'SPARE'):
            self.PlotSPARE(datamodel,plotOptions)
        elif(str(plotOptions['VIEW']) == 'LongitudinalTrend'):
            self.PlotLongitudinalTrends(datamodel,plotOptions)

    def PlotAgeTrends(self,datamodel,plotOptions):
        """Plot Age Trends - default view"""

        currentROI = plotOptions['ROI']
        currentHue = plotOptions['HUE']

        if not currentHue:
            currentHue = 'Sex'

        # clear plot
        self.axes.clear()

        # seaborn plot on axis
        sns.scatterplot(x='Age', y=currentROI,  hue=currentHue,ax=self.axes, s=5,
                       data=datamodel.GetData(currentROI,currentHue))

        # Plot normative range if according GAM model is available
        if (datamodel.harmonization_model is not None) and (currentROI in ['H_' + x for x in datamodel.harmonization_model['ROIs']]):
            x,y,z = datamodel.GetNormativeRange(currentROI[2:])
            print('Pooled variance: %f' % (z))
            # Plot three lines as expected mean and +/- 2 times standard deviation
            sns.lineplot(x=x, y=y, ax=self.axes, linestyle='-', markers=False, color='k')
            sns.lineplot(x=x, y=y+z, ax=self.axes, linestyle=':', markers=False, color='k')
            sns.lineplot(x=x, y=y-z, ax=self.axes, linestyle=':', markers=False, color='k')

        # Set ROI name as y-label if applicable
        _, MUSEDictIDtoNAME = datamodel.GetMUSEDictionaries()
        ylabel = currentROI
        print(currentROI)
        if ylabel.startswith('MUSE_'):
            ylabel = '(MUSE) ' + list(map(MUSEDictIDtoNAME.get, [currentROI]))[0]

        if ylabel.startswith('WMLS_'):
            ylabel = '(WMLS) ' + list(map(MUSEDictIDtoNAME.get, [currentROI.replace('WMLS_', 'MUSE_')]))[0]

        if ylabel.startswith('H_MUSE_'):
            ylabel = '(Harmonized MUSE) ' + list(map(MUSEDictIDtoNAME.get, [currentROI.replace('H_', '')]))[0]
         
        if ylabel.startswith('RES_MUSE_'):
            ylabel = '(Residuals MUSE) ' + list(map(MUSEDictIDtoNAME.get, [currentROI.replace('RES_', '')]))[0]

        self.axes.set(ylabel=ylabel)

        # refresh canvas
        self.draw()

    def PlotSPARE(self,datamodel,plotOptions):
        """Plot SPARE"""
        # clear plot
        self.axes.clear()

        # set hue
        currentHue = plotOptions['HUE']

        if not currentHue:
            currentHue = 'Sex'

        # seaborn plot on axis
        if (('SPARE_AD' in datamodel.GetColumnHeaderNames()) &
            ('SPARE_BA' in datamodel.GetColumnHeaderNames())):
            spare_data = datamodel.GetData(['SPARE_BA','SPARE_AD'],
                                           currentHue)
            spare_data.loc[:, 'SPARE_BA'] = spare_data['SPARE_BA'] - spare_data['Age'] 
            sns.scatterplot(x='SPARE_AD', y='SPARE_BA', hue=currentHue,ax=self.axes,
                            s=5, data=spare_data)
            self.axes.axvline(x=0.0, alpha=0.5, ls='--', color='k')
            self.axes.axhline(y=0.0, alpha=0.5, ls='--', color='k')
            self.axes.text(x=-2, y=0, s='Brain age == chronological age',
                     va='center', ha='center', backgroundcolor='white')
            self.axes.text(x=-2, y=+20., s='Advanced brain brain age',
                        va='center', ha='center', backgroundcolor='white')
            self.axes.text(x=-2, y=-20., s='Resilient brain age',
                        va='center', ha='center', backgroundcolor='white')
            self.axes.arrow(-4, +12.5, 0., +1.7, head_width=.1, head_length=1.3, edgecolor=None, facecolor='k')
            self.axes.arrow(-4, -12.5, 0., -1.7, head_width=.1, head_length=1.3, edgecolor=None, facecolor='k')
            self.axes.set(xlim=[-5, 5], ylim=[-30,40])
        else:
            # Set error text on plot
            self.axes.text(0.5,0.5,'No SPARE-* scores available.',
                           va='center', ha='center')
            print('Plotting failed. Check data set for inclusion of SPARE-* indices.')

        # refresh canvas
        self.draw()

    
    def PlotLongitudinalTrends(self,datamodel,plotOptions):
        """Plot Age Trends - default view"""

        currentROI = plotOptions['ROI']
        currentHue = plotOptions['HUE']
        N_samples=10
        N_timepoints=5
        seed=10

        data=datamodel.GetData(['participant_id',currentROI],
                               currentHue)
        
        # limit dataset by number of timepoints and sample
        data_sample = data.copy()
        data_sample.dropna(subset=[currentROI],inplace=True)
        vc = data_sample['participant_id'].value_counts()
        timepoints = vc[vc >= N_timepoints].index[:]
        data_sample = data_sample[data_sample['participant_id'].isin(timepoints)]
        random.seed(seed)
        sampled_list = random.sample(list(data_sample['participant_id']), N_samples)
        data_sample = data_sample[data_sample['participant_id'].isin(sampled_list)]
        
        if not currentHue:
            currentHue = 'Sex'

        # clear plot
        self.axes.clear()

        # longitudinal plot harmonized
        _, ax = plt.subplots(1,1)
        ax = sns.scatterplot(x='Age',y=currentROI,hue=currentHue,ax=self.axes,linewidth=1.5,s=50,data=data_sample)
        for i in data_sample['participant_id']:
            d = data_sample.index[data_sample['participant_id'] == i].tolist()
            ax.plot(data_sample['Age'][d],data_sample[currentROI][d],c='0',linewidth=2)

        # Set ROI name as y-label if applicable
        _, MUSEDictIDtoNAME = datamodel.GetMUSEDictionaries()
        ylabel = currentROI
        print(currentROI)
        if ylabel.startswith('MUSE_'):
            ylabel = '(MUSE) ' + list(map(MUSEDictIDtoNAME.get, [currentROI]))[0]

        if ylabel.startswith('WMLS_'):
            ylabel = '(WMLS) ' + list(map(MUSEDictIDtoNAME.get, [currentROI.replace('WMLS_', 'MUSE_')]))[0]

        if ylabel.startswith('H_MUSE_'):
            ylabel = '(Harmonized MUSE) ' + list(map(MUSEDictIDtoNAME.get, [currentROI.replace('H_', '')]))[0]

        if ylabel.startswith('RES_MUSE_'):
            ylabel = '(Residuals MUSE) ' + list(map(MUSEDictIDtoNAME.get, [currentROI.replace('RES_', '')]))[0]
         
        self.axes.set(ylabel=ylabel)

        # refresh canvas
        self.draw()


    def Reset(self):
        """Remove all plots"""
        self.axes.clear()
