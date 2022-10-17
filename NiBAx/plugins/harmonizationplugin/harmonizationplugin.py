from PyQt5.QtGui import *
from PyQt5 import QtGui, QtCore, QtWidgets, uic
import sys, os
import neuroHarmonize as nh
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as pat
import numpy as np
import pandas as pd
import re
from NiBAx.core.plotcanvas import PlotCanvas
from NiBAx.core.baseplugin import BasePlugin
from NiBAx.core.gui.SearchableQComboBox import SearchableQComboBox
from NiBAx.plugins.harmonizationplugin.harmonization import harmonize

from NiBAx.core import iStagingLogger

logger = iStagingLogger.get_logger(__name__)

class harmonizationplugin(QtWidgets.QWidget,BasePlugin):

    #constructor
    def __init__(self):
        super(harmonizationplugin,self).__init__()
        root = os.path.dirname(__file__)
        self.readAdditionalInformation(root)
        self.ui = uic.loadUi(os.path.join(root, 'harmonization.ui'),self)
        self.ui.Harmonization_Model_Loaded_Lbl.setHidden(True)
        self.ui.comboBoxROI = SearchableQComboBox(self.ui)
        self.plotCanvas = PlotCanvas(self.ui.page_2)
        self.plotCanvas.axes1 = self.plotCanvas.fig.add_subplot(131)
        self.plotCanvas.axes2 = self.plotCanvas.fig.add_subplot(132)
        self.plotCanvas.axes3 = self.plotCanvas.fig.add_subplot(133)
        self.ui.horizontalLayout_4.insertWidget(0,self.plotCanvas) 
        self.ui.horizontalLayout_3.insertWidget(0,self.comboBoxROI)

        self.ui.stackedWidget.setCurrentIndex(0) 


    def getUI(self):
        return self.ui
    
    def SetupConnections(self):
        self.ui.load_harmonization_model_Btn.clicked.connect(lambda: self.OnLoadHarmonizationModelBtnClicked())
        if self.datamodel.data is None:
            self.ui.load_harmonization_model_Btn.setEnabled(False)
            self.ui.Harmonized_Data_Information_Lbl.setText('Data must be loaded before model selection.\nReturn to Load and Save Data tab to select data.')
        self.ui.load_other_model_Btn.clicked.connect(lambda: self.OnLoadHarmonizationModelBtnClicked())
        self.ui.show_data_Btn.clicked.connect(lambda: self.OnShowDataBtnClicked())
        self.ui.apply_model_to_dataset_Btn.clicked.connect(lambda: self.OnApplyModelToDatasetBtnClicked())
        self.ui.add_to_dataframe_Btn.clicked.connect(lambda: self.OnAddToDataFrame())
        self.ui.comboBoxROI.currentIndexChanged.connect(self.UpdatePlot)
        self.ui.add_to_dataframe_Btn.setStyleSheet("background-color: rgb(230,255,230); color: black")
        self.datamodel.data_changed.connect(lambda: self.OnDataChanged())
        self.ui.apply_model_to_dataset_Btn.setEnabled(False)

        if ('RES_MUSE_Volume_47' in self.datamodel.GetColumnHeaderNames() and
            'RAW_RES_MUSE_Volume_47' in self.datamodel.GetColumnHeaderNames()):
            self.ui.show_data_Btn.setEnabled(True)
            self.ui.show_data_Btn.setStyleSheet("background-color: rgb(230,230,255); color: black")
        else:
            self.ui.show_data_Btn.setEnabled(False)
    
    def LoadHarmonizationModel(self, filename):
        self.filename = os.path.basename(filename)

        if filename == "":
            text_1=('Harmonization model not selected')
            self.ui.Harmonized_Data_Information_Lbl.setText(text_1)
            self.ui.Harmonized_Data_Information_Lbl.setObjectName('Missing_label')
            self.ui.Harmonized_Data_Information_Lbl.setStyleSheet('QLabel#Missing_label {color: red}')
        else:
            self.datamodel.harmonization_model = pd.read_pickle(filename)
            if not (isinstance(self.datamodel.harmonization_model,dict) and 'SITE_labels' in self.datamodel.harmonization_model):
                text_2=('Selected file is not a viable harmonization model')
                self.ui.Harmonized_Data_Information_Lbl.setText(text_2)
                self.ui.Harmonized_Data_Information_Lbl.setObjectName('Error_label')
                self.ui.Harmonized_Data_Information_Lbl.setStyleSheet('QLabel#Error_label {color: red}')
            else:
                self.ui.Harmonization_Model_Loaded_Lbl.setHidden(False)
                self.ui.Harmonization_Model_Loaded_Lbl.setObjectName('correct_label')
                self.ui.Harmonization_Model_Loaded_Lbl.setStyleSheet('QLabel#correct_label {color: green}')
                self.ui.Harmonization_Model_Loaded_Lbl.setText('Harmonization model compatible')
                self.ui.Harmonized_Data_Information_Lbl.setObjectName('correct_label')
                self.ui.Harmonized_Data_Information_Lbl.setStyleSheet('QLabel#correct_label {color: black}')
                model_text1 = (os.path.basename(filename) +' loaded')
                model_text2 = ('SITES in training set: '+ ' '.join([str(elem) for elem in list(self.datamodel.harmonization_model['SITE_labels'])]))
                model_text2 = wrap_by_word(model_text2,4)
                model_text1 += '\n\n'+model_text2
                if 'Covariates' in self.datamodel.harmonization_model:
                    covariates = self.datamodel.harmonization_model['Covariates']
                    model_text3 = ('Harmonization Covariates: '+ str(covariates))
                    model_text1 += '\n'+model_text3
                else:
                    model_text3 = ('Harmonization Covariates Unavailable')
                    model_text1 += '\n'+model_text3
                age_max = self.datamodel.harmonization_model['smooth_model']['bsplines_constructor'].knot_kwds[0]['upper_bound']
                age_min = self.datamodel.harmonization_model['smooth_model']['bsplines_constructor'].knot_kwds[0]['lower_bound']
                model_text4 = ('Valid Age Range: [' + str(age_min) + ', ' + str(age_max) + ']')
                model_text1 += '\n'+model_text4
                self.ui.Harmonized_Data_Information_Lbl.setText(model_text1)
                if self.datamodel.data is None:
                    self.ui.apply_model_to_dataset_Btn.setEnabled(False)
                    self.ui.Harmonized_Data_Information_Lbl.setText('Data must be loaded before model selection or application.\nReturn to Load and Save Data tab to select data.')
                else:
                    self.ui.apply_model_to_dataset_Btn.setEnabled(True)
                    self.ui.apply_model_to_dataset_Btn.setStyleSheet("background-color: rgb(230,255,230); color: black")
        self.ui.stackedWidget.setCurrentIndex(0)

    def OnLoadHarmonizationModelBtnClicked(self):
        self.filename, _ = QtWidgets.QFileDialog.getOpenFileName(None,
        'Open harmonization model file',
        QtCore.QDir().homePath(),
        "Pickle files (*.pkl.gz *.pkl)")

        self.LoadHarmonizationModel(self.filename)
    
    def PopulateROI(self):
        MUSEDictDataFrame = self.datamodel.GetMUSEDictDataFrame()
        _, MUSEDictIDtoNAME = self.datamodel.GetMUSEDictionaries()
        roiList = list(set(self.datamodel.GetColumnHeaderNames()).intersection(set(MUSEDictDataFrame[MUSEDictDataFrame['ROI_LEVEL']=='SINGLE']['ROI_COL'])))
        roiList.sort()
        roiList = ['(MUSE) ' + list(map(MUSEDictIDtoNAME.get, [k]))[0] if k.startswith('MUSE_') else k for k in roiList]
        
        if ('MUSE_Volume_301' in list(self.datamodel.harmonization_model['ROIs'])):
            logger.info('Model includes derived volumes')
            derivedROIs = list(set(self.datamodel.GetColumnHeaderNames()).intersection(set(MUSEDictDataFrame[MUSEDictDataFrame['ROI_LEVEL']=='DERIVED']['ROI_COL'])))
            derivedROIs.sort()
            derivedROIs = ['(MUSE) ' + list(map(MUSEDictIDtoNAME.get, [k]))[0] if k.startswith('MUSE_') else k for k in derivedROIs]
            roiList = roiList + derivedROIs
        else:
            logger.info('No derived volumes in model')

        #add the list items to comboBox
        self.ui.comboBoxROI.blockSignals(True)
        self.ui.comboBoxROI.clear()
        self.ui.comboBoxROI.blockSignals(False)
        self.ui.comboBoxROI.addItems(roiList)

    def OnShowDataBtnClicked(self):
            self.MUSE = self.datamodel.data
            self.PopulateROI()
    
    def OnApplyModelToDatasetBtnClicked(self):
        self.MUSE, self.parameters= harmonize.DoHarmonization(self)
        self.PopulateROI()

    def UpdatePlot(self):

        #get current selected combobox item
        currentROI = self.ui.comboBoxROI.currentText()

        # Translate ROI name back to ROI ID
        AllItems = [self.ui.comboBoxROI.itemText(i) for i in range(self.ui.comboBoxROI.count())]
        MUSEDictNAMEtoID, _ = self.datamodel.GetMUSEDictionaries()
        if currentROI not in AllItems[:-1]:
            self.ui.comboBoxROI.blockSignals(True)
            self.ui.comboBoxROI.clear()
            self.ui.comboBoxROI.blockSignals(False)
            self.ui.comboBoxROI.addItems(AllItems[:-1])
            currentROI = self.ui.comboBoxROI.itemText(0)
            self.ui.comboBoxROI.setCurrentText(currentROI)
            print("Invalid input. Setting to %s." % (currentROI))
        
        currentROI = list(map(MUSEDictNAMEtoID.get, [currentROI[7:]]))[0]      

        #create empty dictionary of plot options
        plotOptions = dict()

        #fill dictionary with options
        plotOptions['ROI'] = currentROI

        self.plotMUSE(plotOptions)

    def plotMUSE(self,plotOptions):
        self.ui.stackedWidget.setCurrentIndex(1)

        self.plotCanvas.axes1.clear()
        self.plotCanvas.axes2.clear()
        self.plotCanvas.axes3.clear()

        # select roi
        currentROI = plotOptions['ROI']
        h_res = 'RES_'+currentROI
        raw_res = 'RAW_RES_'+currentROI
        selected_gamma = 'gamma_'+currentROI
        selected_delta = 'delta_'+currentROI
        
        if 'isTrainMUSEHarmonization' in self.MUSE: 
            print('Plotting controls only')
            data = self.MUSE[self.MUSE['isTrainMUSEHarmonization']==1]
        else: 
            data = self.MUSE
            data.dropna(subset=[raw_res],inplace=True)

        data.loc[:,'SITE'] = pd.Categorical(data['SITE'])
        data.loc[:,'SITE'] = data.SITE.cat.remove_unused_categories()

        # make palette
        if 'SITE_colors' in self.datamodel.harmonization_model:
            print('Creating color palette from model...')
            cSite = self.datamodel.harmonization_model['SITE_colors'] 
            wanted = set(data.SITE.unique()).intersection(set(self.datamodel.harmonization_model['SITE_labels']))
            cSite = { your_key: cSite[your_key] for your_key in wanted }
            site_extra = list(set(data.SITE.unique())-set(self.datamodel.harmonization_model['SITE_labels']))
            palette_extra= sns.color_palette("Set2", n_colors=len(site_extra))
            cSite_extra = dict(zip(site_extra,palette_extra))
            cSite.update(cSite_extra)
        else:
            print('Color palette not available in model. Creating new color palette...')
            colors=sns.color_palette("cubehelix", n_colors=len(list(data.SITE.unique())))
            cSite = dict(zip(list(data.SITE.unique()),colors))
        
        labels = sorted([x + ' (N=' for x in list(cSite.keys())])

        sd_raw = data[raw_res].std()
        sd_h = data[h_res].std()

        ci_plus_raw = 0.65*sd_raw
        ci_minus_raw = -0.65*sd_raw

        ci_plus_h = 0.65*sd_h
        ci_minus_h = -0.65*sd_h

        PROPS = {
            'boxprops':{'edgecolor':'none'},
            'medianprops':{'color':'black'},
            'whiskerprops':{'color':'black'},
            'capprops':{'color':'black'}
        }

        parameters = self.parameters 
        parameters = parameters[parameters.index.isin(list(cSite.keys()))]
        parameters['SITE']=parameters.index
        gamma_values = [x for x in parameters[selected_gamma].values.round(3).tolist()]
        gamma_values = [str("{:.3f}".format(x)) for x in gamma_values]
        delta_values = [x for x in parameters[selected_delta].values.round(3).tolist()]
        delta_values = [str("{:.3f}".format(x)) for x in delta_values]
        parameters.loc[:,'gamma_values'] = gamma_values
        parameters.loc[:,'delta_values'] = delta_values
        
        self.plotCanvas.axes1.get_figure().set_tight_layout(True)
        self.plotCanvas.axes1.set_xlim(-4*sd_raw, 4*sd_raw)
        sns.set(style='white')
        a = sns.boxplot(x=raw_res, y="SITE", data=data, palette=cSite,linewidth=.25,showfliers = False,ax=self.plotCanvas.axes1,**PROPS)
        nobs1 = data['SITE'].value_counts().sort_index(ascending=True).values
        nobs1 = [str(x) for x in nobs1.tolist()]
        nobs1 = [i for i in nobs1]
        labels = [''.join(i) for i in zip(labels, nobs1)]
        labels = [x + ')' for x in labels]
        self.plotCanvas.axes1.axvline(ci_plus_raw,color='grey',ls='--')
        self.plotCanvas.axes1.axvline(ci_minus_raw,color='grey',ls='--')
        self.plotCanvas.axes1.yaxis.set_ticks_position('left')
        self.plotCanvas.axes1.xaxis.set_ticks_position('bottom')
        a.tick_params(axis='both', which='major', length=4)
        a.set_xlabel('Residuals before harmonization')

        self.plotCanvas.axes2.get_figure().set_tight_layout(True)
        upper_limit = np.nanmax(parameters[selected_gamma]+parameters[selected_delta])
        lower_limit = np.nanmin(parameters[selected_gamma]-parameters[selected_delta])
        limit = max(abs(upper_limit),abs(lower_limit)) 
        self.plotCanvas.axes2.set_xlim(-limit,limit)
        self.plotCanvas.axes2.set_ylim(self.plotCanvas.axes1.get_ylim())
        sns.set(style='white')
        self.plotCanvas.axes2.errorbar(x=parameters[selected_gamma],y=parameters['SITE'],xerr=parameters[selected_delta],ecolor='black',elinewidth=0.25,capsize=0.25,zorder=-1,fmt='none')
        kws = {"s": 4, "facecolor": "black", "linewidth": 0.5}
        color = parameters[parameters[selected_gamma].notna()]['SITE'].map(cSite)
        b = sns.scatterplot(x=selected_gamma,y='SITE',data=parameters.reset_index(),marker='s',edgecolor=color,zorder=1,**kws,ax=self.plotCanvas.axes2,legend=False)
        b.text(-0.05,self.plotCanvas.axes2.get_yticks()[0]-1.3,'Location (\u03B3*)',ha='right',fontsize='small')
        b.text(0,self.plotCanvas.axes2.get_yticks()[0]-1.3,'|',ha='center',fontsize='small')
        b.text(0.05,self.plotCanvas.axes2.get_yticks()[0]-1.3,'Scale (\u03B4*)',ha='left',fontsize='small')
        for count,site in enumerate(parameters['SITE']):
            self.plotCanvas.axes2.get_yticks()
            if 'nan' in parameters.loc[site]['gamma_values']:
                b.text(-0.05,self.plotCanvas.axes2.get_yticks()[count]-0.2,' nan',fontsize='x-small',ha='right')
            else:
                b.text(-0.05,self.plotCanvas.axes2.get_yticks()[count]-0.2,parameters.loc[site]['gamma_values'],fontsize='x-small',ha='right')
                b.text(0.05,self.plotCanvas.axes2.get_yticks()[count]-0.2,parameters.loc[site]['delta_values'],fontsize='x-small',ha='left')
        b.set_xlabel('')
        b.set_ylabel('')
        b.set(yticklabels=[])
        self.plotCanvas.axes2.xaxis.set_ticks_position('bottom')
        b.tick_params(axis='both',left=False,right=False, length=4)
        self.plotCanvas.axes2.axvline(0,color='black',linewidth=0.25)
        sns.despine(ax=self.plotCanvas.axes2, left=True)

        # get title as ROI name relative to scale/shift label
        _, MUSEDictIDtoNAME = self.datamodel.GetMUSEDictionaries()
        title = currentROI
        if title.startswith('MUSE_'):
            title = '(MUSE) ' + list(map(MUSEDictIDtoNAME.get, [currentROI]))[0]

        if title.startswith('WMLS_'):
            title = '(WMLS) ' + list(map(MUSEDictIDtoNAME.get, [currentROI.replace('WMLS_', 'MUSE_')]))[0]

        self.plotCanvas.axes2.get_figure().subplots_adjust(top=.8)
        self.plotCanvas.axes2.get_figure().suptitle(title)
        
        
        self.plotCanvas.axes3.get_figure().set_tight_layout(True)
        self.plotCanvas.axes3.set_xlim(-4*sd_raw, 4*sd_raw)
        self.plotCanvas.axes3.set_ylim( self.plotCanvas.axes1.get_ylim() )
        sns.set(style='white')
        c = sns.boxplot(x=h_res, y="SITE", data=data, palette=cSite,linewidth=0.25,showfliers = False,ax=self.plotCanvas.axes3,**PROPS)
        nobs2 = data['SITE'].value_counts().sort_index(ascending=True).values
        nobs2 = [str(x) for x in nobs2.tolist()]
        nobs2 = [i for i in nobs2]
        if nobs1 != nobs2:
            print('not equal sample sizes')
        a.set_yticklabels(labels)
        self.plotCanvas.axes3.axvline(ci_plus_h,color='grey',ls='--')
        self.plotCanvas.axes3.axvline(ci_minus_h,color='grey',ls='--')
        self.plotCanvas.axes3.yaxis.set_ticks_position('left')
        self.plotCanvas.axes3.xaxis.set_ticks_position('bottom')
        c.tick_params(axis='both', which='major', length=4)
        c.set_xlabel('Residuals after harmonization')
        c.set_ylabel('')
        c.set(yticklabels=[])
        sns.despine(ax=self.plotCanvas.axes1, trim=True)
        sns.despine(ax=self.plotCanvas.axes3, trim=True)

        self.plotCanvas.draw()

    def OnAddToDataFrame(self):
        print('Saving modified data to pickle file...')

        self.MUSE.set_index(self.datamodel.data.index,inplace=True)

        ROI_list = list(self.datamodel.harmonization_model['ROIs'])
        if ('MUSE_Volume_301' not in ROI_list):
            logger.info('No derived volumes in model')
            MUSEDictDataFrame= self.datamodel.GetMUSEDictDataFrame()
            Derived_numbers = list(MUSEDictDataFrame[MUSEDictDataFrame['ROI_LEVEL']=='DERIVED']['ROI_INDEX'])
            Derived_MUSE_Volumes = list('MUSE_Volume_' + str(x) for x in Derived_numbers)
            ROI_list = ROI_list + Derived_MUSE_Volumes
            ROI_list.remove('MUSE_Volume_702')
        else:
            logger.info('Model includes derived volumes')
        H_ROIs = list('H_' + str(x) for x in ROI_list)
        ROIs_ICV_Sex_Residuals = ['RES_ICV_Sex_' + x for x in self.datamodel.harmonization_model['ROIs']]
        ROIs_Residuals = ['RES_' + x for x in self.datamodel.harmonization_model['ROIs']]
        RAW_Residuals = ['RAW_RES_' + x for x in self.datamodel.harmonization_model['ROIs']]
        if ('H_MUSE_Volume_47' not in self.datamodel.data.keys()):
            self.datamodel.data.loc[:,H_ROIs] = self.MUSE[H_ROIs]
        self.datamodel.data.loc[:,ROIs_ICV_Sex_Residuals] = self.MUSE[ROIs_ICV_Sex_Residuals]
        self.datamodel.data.loc[:,ROIs_Residuals] = self.MUSE[ROIs_Residuals]
        self.datamodel.data.loc[:,RAW_Residuals] = self.MUSE[RAW_Residuals]
        self.datamodel.data_changed.emit()
    
    def OnDataChanged(self):
        self.ui.stackedWidget.setCurrentIndex(0)
        self.plotCanvas.axes1.clear()
        self.plotCanvas.axes2.clear()
        self.plotCanvas.axes3.clear()
        self.MUSE=None
        if ('RES_MUSE_Volume_47' in self.datamodel.GetColumnHeaderNames() and
            'RAW_RES_MUSE_Volume_47' in self.datamodel.GetColumnHeaderNames()):
            self.ui.show_data_Btn.setEnabled(True)
            self.ui.show_data_Btn.setStyleSheet("background-color: lightBlue; color: white")
        else:
            self.ui.show_data_Btn.setEnabled(False)
    
        if self.datamodel.data is None:
            self.ui.load_harmonization_model_Btn.setEnabled(False)
            self.ui.apply_model_to_dataset_Btn.setEnabled(False)
            self.ui.Harmonized_Data_Information_Lbl.setText('Data must be loaded before model selection.\nReturn to Load and Save Data tab to select data.')
        else:
            self.ui.load_harmonization_model_Btn.setEnabled(True)
            if self.datamodel.harmonization_model is None:
                self.ui.apply_model_to_dataset_Btn.setEnabled(False)
                self.ui.Harmonized_Data_Information_Lbl.setText('No harmonization model has been selected')
            else:
                self.ui.apply_model_to_dataset_Btn.setEnabled(True)
                self.ui.apply_model_to_dataset_Btn.setStyleSheet("background-color: rgb(230,255,230); color: black")
                self.ui.Harmonized_Data_Information_Lbl.setObjectName('correct_label')
                self.ui.Harmonized_Data_Information_Lbl.setStyleSheet('QLabel#correct_label {color: black}')
                model_text1 = (self.filename +' loaded')
                model_text2 = ('SITES in training set: '+ ' '.join([str(elem) for elem in list(self.datamodel.harmonization_model['SITE_labels'])]))
                model_text2 = wrap_by_word(model_text2,4)
                model_text1 += '\n\n'+model_text2
                if 'Covariates' in self.datamodel.harmonization_model:
                    covariates = self.datamodel.harmonization_model['Covariates']
                    model_text3 = ('Harmonization Covariates: '+ str(covariates))
                    model_text1 += '\n'+model_text3
                else:
                    model_text3 = ('Harmonization Covariates Unavailable')
                    model_text1 += '\n'+model_text3
                age_max = self.datamodel.harmonization_model['smooth_model']['bsplines_constructor'].knot_kwds[0]['upper_bound']
                age_min = self.datamodel.harmonization_model['smooth_model']['bsplines_constructor'].knot_kwds[0]['lower_bound']
                model_text4 = ('Valid Age Range: [' + str(age_min) + ', ' + str(age_max) + ']')
                model_text1 += '\n'+model_text4
                self.ui.Harmonized_Data_Information_Lbl.setText(model_text1)

def wrap_by_word(s, n):
    a = s.split()
    ret = ''
    for i in range(0, len(a), n):
        ret += ' '.join(a[i:i+n]) + '\n'

    return ret
