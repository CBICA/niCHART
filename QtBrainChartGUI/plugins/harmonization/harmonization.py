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
        self.datamodel.data_changed.connect(lambda: self.OnDataChanged())
        self.ui.apply_model_to_dataset_Btn.setEnabled(False) # until function is implemented

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
            print("Harmonization model not selected")
        else:
            self.model = pd.read_pickle(filename)
            if not (isinstance(self.model,dict) and 'SITE_labels' in self.model):
                print('Selected file is not a viable harmonization model')
            else:
                self.MUSE = DoHarmonization(self.datamodel.data,self.model)
                self.plotMUSE()

    def OnShowDataBtnClicked(self):
        self.MUSE = self.datamodel.data[['SITE','RES_MUSE_Volume_47','RAW_RES_MUSE_Volume_47']]
        self.plotMUSE()
    
    def OnApplyModelToDatasetBtnClicked(self):
        pass

    def plotMUSE(self):
        self.ui.stackedWidget.setCurrentIndex(1)

        if 'isTrainMUSEHarmonization' in self.MUSE:  ###placeholder for the time being until I can implement a dropdown menu for dataselection 
            print('Plotting controls only')
            self.MUSE = self.MUSE[self.MUSE['isTrainMUSEHarmonization']==1]
        else:
            self.MUSE.dropna(subset=['RAW_RES_MUSE_Volume_47'],inplace=True)

        self.MUSE['SITE'] = pd.Categorical(self.MUSE['SITE'])
        self.MUSE['SITE'] = self.MUSE.SITE.cat.remove_unused_categories()

        sd_raw = self.MUSE['RAW_RES_MUSE_Volume_47'].std()
        sd_h = self.MUSE['RES_MUSE_Volume_47'].std()

        ci_plus_raw = 0.65*sd_raw
        ci_minus_raw = -0.65*sd_raw

        ci_plus_h = 0.65*sd_h
        ci_minus_h = -0.65*sd_h

        
        upper_limit = self.MUSE['RAW_RES_MUSE_Volume_47'].max()
        lower_limit = self.MUSE['RAW_RES_MUSE_Volume_47'].min()
        plt.ylim(lower_limit-1000, upper_limit+1000)
        sns.set(style='white')
        a = sns.stripplot(x="SITE", y='RAW_RES_MUSE_Volume_47', data=self.MUSE, palette=sns.color_palette("hls", 21),linewidth=1,ax=self.plotCanvas.axes1)
        a = sns.boxplot(x="SITE", y='RAW_RES_MUSE_Volume_47', data=self.MUSE, palette=sns.color_palette("hls", 21),ax=self.plotCanvas.axes1)
        medians = self.MUSE.groupby(['SITE'])['RAW_RES_MUSE_Volume_47'].median().values
        nobs = self.MUSE['SITE'].value_counts().sort_index(ascending=True).values
        nobs = [str(x) for x in nobs.tolist()]
        nobs = [i for i in nobs]
        # Add it to the plot
        pos = range(len(nobs))
        for tick,label in zip(pos,a.get_xticklabels()):
            a.text(pos[tick],
                    medians[tick] + 0.03,
                    nobs[tick],
                    horizontalalignment='center',
                    size='x-small',
                    color='w',
                    weight='semibold')
        a.axhline(ci_plus_raw,color='red')
        a.axhline(ci_minus_raw,color='red')
        a.tick_params(axis='x', rotation=60)
        a.set_title('Raw ROI (Y) - Predicted Mean (f_k)')
        
        h_upper_limit = self.MUSE['RES_MUSE_Volume_47'].max()
        h_lower_limit = self.MUSE['RES_MUSE_Volume_47'].min()
        plt.ylim(h_lower_limit-1000, h_upper_limit+1000)
        sns.set(style='white')
        b = sns.stripplot(x="SITE", y='RES_MUSE_Volume_47', data=self.MUSE, palette=sns.color_palette("hls", 21),linewidth=1,ax=self.plotCanvas.axes2)
        b = sns.boxplot(x="SITE", y='RES_MUSE_Volume_47', data=self.MUSE, palette=sns.color_palette("hls", 21),ax=self.plotCanvas.axes2)
        medians = self.MUSE.groupby(['SITE'])['RES_MUSE_Volume_47'].median().values
        nobs = self.MUSE['SITE'].value_counts().sort_index(ascending=True).values
        nobs = [str(x) for x in nobs.tolist()]
        nobs = [i for i in nobs]
        # Add it to the plot
        pos = range(len(nobs))
        for tick,label in zip(pos,a.get_xticklabels()):
            b.text(pos[tick],
                    medians[tick] + 0.03,
                    nobs[tick],
                    horizontalalignment='center',
                    size='x-small',
                    color='w',
                    weight='semibold')
        b.axhline(ci_plus_h,color='red')
        b.axhline(ci_minus_h,color='red')
        b.tick_params(axis='x', rotation=60)
        b.set_title('Harmonized ROI (Y) - Predicted Mean (f_k)')

    def OnAddToDataFrame(self):
        print('Saving modified data to pickle file...')

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


def DoHarmonization(data, model):
    print('Running harmonization.')

    data['Sex'] = data['Sex'].map({'M':1,'F':0})
    covars = data[['SITE','Age','Sex','DLICV_baseline']].copy()
    covars.loc[covars.Age>100, 'Age']=100
    bayes_data, stand_mean = nh.harmonizationApply(data[[x for x in model['ROIs']]].values,
                                            covars,
                                            model,True)

    Raw_ROIs_Residuals = data[model['ROIs']].values - stand_mean

    # create list of new SITEs to loop through
    new_sites = set(data['SITE'].value_counts().index.tolist())^set(model['SITE_labels'])

    var_pooled = model['var_pooled']

    if 'UseForComBatGAMHarmonization' in data.columns:
        for site in new_sites:
            missing = np.array(data['SITE']==site,dtype=bool)
            training = np.array(data['UseForComBatGAMHarmonization'],dtype=bool)
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
        print('Skipping out-of-sample harmonization because `UseForComBatGAMHarmonization` does not existexists.')


    if ('H_MUSE_Volume_47' not in data.keys()):
        data = pd.concat([data.reset_index(), pd.DataFrame(bayes_data, columns=['H_' + s for s in model['ROIs']])],
                        axis=1)    
    start_index = len(model['SITE_labels'])
    sex_icv_effect = np.dot(data[['Sex','DLICV_baseline']],model['B_hat'][start_index:(start_index+2),:])
    ROIs_ICV_Sex_Residuals = ['RES_ICV_Sex_' + x for x in model['ROIs']]
    data[ROIs_ICV_Sex_Residuals] = data[['H_' + x for x in model['ROIs']]] - sex_icv_effect

    data['Sex'] = data['Sex'].map({1:'M',0:'F'})
    ROIs_Residuals = ['RES_' + x for x in model['ROIs']]
    RAW_Residuals = ['RAW_RES_' + x for x in model['ROIs']]
    data[ROIs_Residuals] = bayes_data-stand_mean
    data[RAW_Residuals] = Raw_ROIs_Residuals
    print('Harmonization done.')

    return data
