from PyQt5.QtGui import *
from yapsy.IPlugin import IPlugin
from PyQt5 import QtGui, QtCore, QtWidgets, uic
import sys, os
import neuroHarmonize as nh

import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from QtBrainChartGUI.core.plotcanvas import PlotCanvas

class Harmonization(QtWidgets.QWidget,IPlugin):

    #constructor
    def __init__(self):
        super(Harmonization,self).__init__()
        self.datamodel = None
        root = os.path.dirname(__file__)
        self.ui = uic.loadUi(os.path.join(root, 'harmonization.ui'),self)
        Harmonized_Data_Information_Lbl = QtWidgets.QLabel(self)
        self.plotCanvas = PlotCanvas(self.ui.page_2)
        self.plotCanvas.axes1 = self.plotCanvas.fig.add_subplot(121)
        self.plotCanvas.axes2 = self.plotCanvas.fig.add_subplot(122)
        self.ui.verticalLayout.addWidget(self.plotCanvas) 
        self.MUSE = None

        self.ui.stackedWidget.setCurrentIndex(0) 


    def getUI(self):
        return self.ui

    def SetupConnections(self):
        self.ui.load_harmonization_model_Btn.clicked.connect(lambda: self.OnLoadHarmonizationModelBtnClicked())
        self.ui.load_other_model_Btn.clicked.connect(lambda: self.OnLoadHarmonizationModelBtnClicked())
        self.ui.show_data_Btn.clicked.connect(lambda: self.OnShowDataBtnClicked())
        self.ui.apply_model_to_dataset_Btn.clicked.connect(lambda: self.OnApplyModelToDatasetBtnClicked())
        self.ui.add_to_dataframe_Btn.clicked.connect(lambda: self.OnAddToDataFrame())
        self.ui.add_to_dataframe_Btn.setStyleSheet("background-color: green; color: white")
        self.datamodel.data_changed.connect(lambda: self.OnDataChanged())
        self.ui.apply_model_to_dataset_Btn.setEnabled(False)

        if ('MUSE_Volume_47' in self.datamodel.GetColumnHeaderNames() and
            'H_MUSE_Volume_47' in self.datamodel.GetColumnHeaderNames()):
            self.ui.show_data_Btn.setEnabled(True)
        else:
            self.ui.show_data_Btn.setEnabled(False)

    def OnLoadHarmonizationModelBtnClicked(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(None,
        'Open harmonization model file',
        QtCore.QDir().homePath(),
        "Pickle files (*.pkl.gz *.pkl)")

        if filename == "":
            text_1=('Harmonization model not selected')
            self.ui.Harmonized_Data_Information_Lbl.setText(text_1)
            self.ui.Harmonized_Data_Information_Lbl.setObjectName('Missing_label')
            self.ui.Harmonized_Data_Information_Lbl.setStyleSheet('QLabel#Missing_label {color: red}')
        else:
            self.model = pd.read_pickle(filename)
            if not (isinstance(self.model,dict) and 'SITE_labels' in self.model):
                text_2=('Selected file is not a viable harmonization model')
                self.ui.Harmonized_Data_Information_Lbl.setText(text_2)
                self.ui.Harmonized_Data_Information_Lbl.setObjectName('Error_label')
                self.ui.Harmonized_Data_Information_Lbl.setStyleSheet('QLabel#Error_label {color: red}')
            else:
                self.ui.Harmonized_Data_Information_Lbl.setObjectName('correct_label')
                self.ui.Harmonized_Data_Information_Lbl.setStyleSheet('QLabel#correct_label {color: black}')
                model_text1 = (os.path.basename(filename) +' loaded')
                model_text2 = ('SITES in training set: '+ ' '.join([str(elem) for elem in list(self.model['SITE_labels'])]))
                model_text2 = wrap_by_word(model_text2,4)
                model_text1 += '\n\n'+model_text2
                age_max = self.model['smooth_model']['bsplines_constructor'].knot_kwds[0]['upper_bound']
                age_min = self.model['smooth_model']['bsplines_constructor'].knot_kwds[0]['lower_bound']
                model_text3 = ('Valid Age Range: [' + str(age_min) + ', ' + str(age_max) + ']')
                model_text1 += '\n'+model_text3
                self.ui.Harmonized_Data_Information_Lbl.setText(model_text1)
                self.ui.apply_model_to_dataset_Btn.setEnabled(True)
        self.ui.stackedWidget.setCurrentIndex(0) 

    def OnShowDataBtnClicked(self):
        self.MUSE = self.datamodel.data[['SITE','RES_MUSE_Volume_47','RAW_RES_MUSE_Volume_47']]
        self.plotMUSE(self.MUSE)
    
    def OnApplyModelToDatasetBtnClicked(self):
        self.MUSE= self.DoHarmonization()
        self.plotMUSE()

    def plotMUSE(self):
        self.ui.stackedWidget.setCurrentIndex(1)
        
        if 'isTrainMUSEHarmonization' in self.MUSE:  ###placeholder for the time being until I can implement a dropdown menu for dataselection 
            print('Plotting controls only')
            data = self.MUSE[self.MUSE['isTrainMUSEHarmonization']==1]
            cSite = sns.color_palette("Paired", n_colors=22)
            c = cSite.copy()
            cSite[1:] = c[0:-1]
            cSite[0] = (0.5, 0.5, 0.5)
            cSite[3:] = c[1:-2]
            cSite[2] = (0.3, 0.6,0.8)
            cSite[6:] = c[2:-4]
            cSite[4] = (0.7, 0.9, 0.5)
            cSite[5] = (0.5, 0.9, 0.6)
            cSite[6] = (0.2, 0.7, 0.2)
            cSite[7] = (0.2, 0.5, 0.2)
            cSite[14] = (0.4, 0.05, 0.5)
            cSite[15] = (0.9, 0.8, 0.2)
            cSite[16] = (0.7, 0.6, 0.1)
            cSite[17] = (0.3, 0.3, 0.3)
            cSite[18] = (0.6, 0.1, 0.6)
            cSite[19] = (0.1, 0.6, 0.5)
            cSite[20] = (0.5, 0.2, 0.2)
            cSite[21] = (0.2, 0.2, 0.5)
        else:
            data = self.MUSE
            self.MUSE.dropna(subset=['RAW_RES_MUSE_Volume_47'],inplace=True)
            cSite=sns.color_palette("hls", len(list(self.MUSE.SITE.unique())))

        data['SITE'] = pd.Categorical(data['SITE'])
        data['SITE'] = data.SITE.cat.remove_unused_categories()

        sd_raw = data['RAW_RES_MUSE_Volume_47'].std()
        sd_h = data['RES_MUSE_Volume_47'].std()

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

        self.plotCanvas.axes1.get_figure().set_tight_layout(True)
        self.plotCanvas.axes1.set_xlim(-4*sd_raw, 4*sd_raw)
        sns.set(style='white')
        a = sns.stripplot(x='RAW_RES_MUSE_Volume_47', y="SITE", data=data, palette=cSite,s=2,linewidth=0,ax=self.plotCanvas.axes1)
        a = sns.boxplot(x='RAW_RES_MUSE_Volume_47', y="SITE", data=data, palette=cSite,linewidth=1,showfliers = False,ax=self.plotCanvas.axes1,**PROPS)
        medians = data.groupby(['SITE'])['RAW_RES_MUSE_Volume_47'].median().values
        nobs1 = data['SITE'].value_counts().sort_index(ascending=True).values
        nobs1 = [str(x) for x in nobs1.tolist()]
        nobs1 = [i for i in nobs1]
        labels = [x + ' (N=' for x in self.model['SITE_labels']]
        labels = [''.join(i) for i in zip(labels, nobs1)]
        labels = [x + ')' for x in labels]
        a.axvline(ci_plus_raw,color='grey',ls='--')
        a.axvline(ci_minus_raw,color='grey',ls='--')
        a.tick_params(axis='both', which='both', length=0)
        a.set_xlabel('Hippocampus right (residuals)',fontdict={'fontsize':15})
        a.set_title('Uncorrected',fontdict={'fontsize':15})
        
        self.plotCanvas.axes2.get_figure().set_tight_layout(True)
        self.plotCanvas.axes2.set_xlim(-4*sd_raw, 4*sd_raw)
        sns.set(style='white')
        b = sns.stripplot(x='RES_MUSE_Volume_47', y="SITE", data=data, palette=cSite,s=2,linewidth=0,ax=self.plotCanvas.axes2)
        b = sns.boxplot(x='RES_MUSE_Volume_47', y="SITE", data=data, palette=cSite,linewidth=1,showfliers = False,ax=self.plotCanvas.axes2,**PROPS)
        medians = data.groupby(['SITE'])['RES_MUSE_Volume_47'].median().values
        nobs2 = data['SITE'].value_counts().sort_index(ascending=True).values
        nobs2 = [str(x) for x in nobs2.tolist()]
        nobs2 = [i for i in nobs2]
        if nobs1 != nobs2:
            print('not equal sample sizes')
        a.set_yticklabels(labels)
        b.axvline(ci_plus_h,color='grey',ls='--')
        b.axvline(ci_minus_h,color='grey',ls='--')
        b.set(yticklabels=[])
        b.tick_params(axis='both', which='both', length=0)
        b.set_xlabel('Hippocampus right (residuals)',fontdict={'fontsize':15})
        b.set_ylabel('')
        b.set_title('Corrected for site (location and scale)',fontdict={'fontsize':15})

    def OnAddToDataFrame(self):
        print('Saving modified data to pickle file...')
        H_ROIs = ['H_'+x for x in self.model]
        ROIs_ICV_Sex_Residuals = ['RES_ICV_Sex_' + x for x in self.model['ROIs']]
        ROIs_Residuals = ['RES_' + x for x in self.model['ROIs']]
        RAW_Residuals = ['RAW_RES_' + x for x in self.model['ROIs']]
        self.datamodel.data

    def OnDataChanged(self):
        self.ui.stackedWidget.setCurrentIndex(0)
        self.plotCanvas.axes1.clear()
        self.plotCanvas.axes2.clear()
        self.MUSE=None
        if ('RES_MUSE_Volume_47' in self.datamodel.GetColumnHeaderNames() and
            'RAW_RES_MUSE_Volume_47' in self.datamodel.GetColumnHeaderNames()):
            self.ui.show_data_Btn.setEnabled(True)
        else:
            self.ui.show_data_Btn.setEnabled(False)


    def DoHarmonization(self):
        print('Running harmonization.')

        covars = self.datamodel.data[['SITE','Age','Sex','DLICV_baseline']].copy()
        covars['Sex'] = covars['Sex'].map({'M':1,'F':0})
        covars.loc[covars.Age>100, 'Age']=100
        bayes_data, stand_mean = nh.harmonizationApply(self.datamodel.data[[x for x in self.model['ROIs']]].values,
                                                covars,
                                                self.model,True)

        Raw_ROIs_Residuals = self.datamodel.data[self.model['ROIs']].values - stand_mean

        # create list of new SITEs to loop through
        new_sites = set(self.datamodel.data['SITE'].value_counts().index.tolist())^set(self.model['SITE_labels'])

        var_pooled = self.model['var_pooled']

        if 'UseForComBatGAMHarmonization' in self.datamodel.data.columns:
            for site in new_sites:
                missing = np.array(self.datamodel.data['SITE']==site,dtype=bool)
                training = np.array(self.datamodel.data['UseForComBatGAMHarmonization'],dtype=bool)
                new_site_is_train = np.logical_and(missing, training)

                if np.count_nonzero(new_site_is_train)<25:
                    print('New site `'+site+'` has less than 25 reference data points. Skipping harmonization.')
                    continue

                gamma_hat_site = np.mean(((Raw_ROIs_Residuals[new_site_is_train,:])/np.dot(np.sqrt(var_pooled),np.ones((1,Raw_ROIs_Residuals[new_site_is_train,:].shape[0]))).T),0)
                gamma_hat_site = gamma_hat_site[:,np.newaxis]
                delta_hat_site = pow(np.std(((Raw_ROIs_Residuals[new_site_is_train,:])/np.dot(np.sqrt(var_pooled),np.ones((1,Raw_ROIs_Residuals[new_site_is_train,:].shape[0]))).T),0),2)
                delta_hat_site = delta_hat_site[:,np.newaxis]

                bayes_data[missing,:] = ((Raw_ROIs_Residuals[missing,:]/np.dot(np.sqrt(var_pooled),np.ones((1,Raw_ROIs_Residuals[missing,:].shape[0]))).T) - np.dot(gamma_hat_site,np.ones((1,Raw_ROIs_Residuals[missing,:].shape[0]))).T)*np.dot(np.sqrt(var_pooled),np.ones((1,Raw_ROIs_Residuals[missing,:].shape[0]))).T/np.dot(np.sqrt(delta_hat_site),np.ones((1,Raw_ROIs_Residuals[missing,:].shape[0]))).T + stand_mean[missing,:]
        else:
            print('Skipping out-of-sample harmonization because `UseForComBatGAMHarmonization` does not exist.')

        if 'isTrainMUSEHarmonization' in self.datamodel.data.columns:
            muse = pd.concat([self.datamodel.data['isTrainMUSEHarmonization'],covars, pd.DataFrame(bayes_data, columns=['H_' + s for s in self.model['ROIs']])],axis=1)    
        else:
            muse = pd.concat([covars,pd.DataFrame(bayes_data, columns=['H_' + s for s in self.model['ROIs']])],axis=1)
        start_index = len(self.model['SITE_labels'])
        sex_icv_effect = np.dot(muse[['Sex','DLICV_baseline']],self.model['B_hat'][start_index:(start_index+2),:])
        ROIs_ICV_Sex_Residuals = ['RES_ICV_Sex_' + x for x in self.model['ROIs']]
        muse[ROIs_ICV_Sex_Residuals] = muse[['H_' + x for x in self.model['ROIs']]] - sex_icv_effect

        muse['Sex'] = muse['Sex'].map({1:'M',0:'F'})
        ROIs_Residuals = ['RES_' + x for x in self.model['ROIs']]
        RAW_Residuals = ['RAW_RES_' + x for x in self.model['ROIs']]
        muse[ROIs_Residuals] = bayes_data-stand_mean
        muse[RAW_Residuals] = Raw_ROIs_Residuals
        print('Harmonization done.')

        return muse

def wrap_by_word(s, n):
    a = s.split()
    ret = ''
    for i in range(0, len(a), n):
        ret += ' '.join(a[i:i+n]) + '\n'

    return ret
