from PyQt5.QtGui import *
from PyQt5 import QtGui, QtCore, QtWidgets, uic
import neuroHarmonize as nh
import numpy as np
import pandas as pd

from NiBAx.core import iStagingLogger

logger = iStagingLogger.get_logger(__name__)

class harmonize(QtCore.QObject):
    """This class is an adapter to the worker class."""
    sendprogress = QtCore.pyqtSignal(str, int)
    done = QtCore.pyqtSignal()

    #constructor
    def __init__(self,datamodel, model):
        super(harmonize,self).__init__()
        self.datamodel = datamodel
        self.datamodel.harmonization_model = model
        self.MUSE = None


    def DoHarmonization(self):
        print('Running harmonization.')

        if 'Covariates' in self.datamodel.harmonization_model:
            covariates = self.datamodel.harmonization_model['Covariates']
            logger.info('Covariates hard-coded in model.')
        else:
            covariates = ['SITE','Age','Sex','DLICV_baseline']
            logger.info('Covariates default to `SITE`, `Age`, `Sex`, and `DLICV_baseline`.')

        # create list of new SITEs to loop through
        new_sites = set(self.datamodel.data['SITE'].value_counts().index.tolist())^set(self.datamodel.harmonization_model['SITE_labels'])

        covars = self.datamodel.data[['SITE','Age','Sex','DLICV_baseline']].reset_index(drop=True).copy()
        covars.loc[:,'Sex'] = covars['Sex'].map({'M':1,'F':0})
        covars.loc[covars.Age>100, 'Age']=100

        # Parameter table for plotting 
        gamma_ROIs = ['gamma_'+ x for x in self.datamodel.harmonization_model['ROIs']]
        delta_ROIs = ['delta_'+ x for x in self.datamodel.harmonization_model['ROIs']]
        calculated_gamma = pd.DataFrame([])
        calculated_delta = pd.DataFrame([])

        if 'UseForComBatGAMHarmonization' in self.datamodel.data.columns:
            sites_to_harmonize = []
            for site in new_sites:
                dataToHarmonize = np.array(self.datamodel.data['SITE']==site,dtype=bool)
                training = np.array(self.datamodel.data['UseForComBatGAMHarmonization'].notnull(),dtype=bool)
                new_site_is_train = np.logical_and(dataToHarmonize, training)
                new_site_is_train = new_site_is_train[~np.isnan(new_site_is_train).any(axis=0)]
            
                if np.count_nonzero(new_site_is_train)<5:
                        site_gamma = pd.DataFrame(np.nan,columns=gamma_ROIs,index=[site])
                        calculated_gamma = calculated_gamma.append(site_gamma)
                        site_delta = pd.DataFrame(np.nan,columns=delta_ROIs,index=[site])
                        calculated_delta = calculated_delta.append(site_delta)
                        print('New site `'+site+'` has less than 25 reference data points. Skipping harmonization.')
                        continue
                else: 
                    print('Harmonizing '+ site)  
                    sites_to_harmonize.append(site)
            
            if not sites_to_harmonize:
                print('No new sites that meet out-of-sample harmonization requirement. Proceeding with harmonization.')
                bayes_data, stand_mean = nh.harmonizationApply(self.datamodel.data[[x for x in self.datamodel.harmonization_model['ROIs']]].values,
                                                    covars,
                                                    self.datamodel.harmonization_model,True)
                gamma_ROIs = ['gamma_'+ x for x in self.datamodel.harmonization_model['ROIs']]
                delta_ROIs = ['delta_'+ x for x in self.datamodel.harmonization_model['ROIs']]
                model_gamma= pd.DataFrame(self.datamodel.harmonization_model['gamma_star'],columns=gamma_ROIs,index=[x for x in self.datamodel.harmonization_model['SITE_labels']])
                model_delta = pd.DataFrame(self.datamodel.harmonization_model['delta_star'],columns=delta_ROIs,index=[x for x in self.datamodel.harmonization_model['SITE_labels']])
                parameters = pd.concat([model_gamma,model_delta],axis=1).sort_index()                     
            else:
                oos_data = self.datamodel.data[self.datamodel.data['SITE'].isin(sites_to_harmonize)].dropna(subset=covariates)[[x for x in self.datamodel.harmonization_model['ROIs']]].values
                oos_covars = self.datamodel.data[self.datamodel.data.SITE.isin(sites_to_harmonize)].dropna(subset=covariates)[covariates]
                oos_covars.loc[:,'Sex'] = oos_covars['Sex'].map({'M':1,'F':0})
                self.model, _ = nh.harmonizationLearn(oos_data, oos_covars,
                                                smooth_terms=['Age'],
                                                smooth_term_bounds=(np.floor(np.min(self.datamodel.data.Age)),np.ceil(np.max(self.datamodel.data.Age))),
                                                orig_model=self.datamodel.harmonization_model,seed=20220601)
                bayes_data, stand_mean = nh.harmonizationApply(self.datamodel.data[[x for x in self.datamodel.harmonization_model['ROIs']]].values,
                                                        covars,
                                                        self.model,True)
                gamma_ROIs = ['gamma_'+ x for x in self.model['ROIs']]
                delta_ROIs = ['delta_'+ x for x in self.model['ROIs']]
                model_gamma= pd.DataFrame(self.model['gamma_star'],columns=gamma_ROIs,index=[x for x in self.model['SITE_labels']])
                model_delta = pd.DataFrame(self.model['delta_star'],columns=delta_ROIs,index=[x for x in self.model['SITE_labels']])                                                
                parameters = pd.concat([model_gamma,model_delta],axis=1).sort_index()
        else:
            print('Skipping out-of-sample harmonization because `UseForComBatGAMHarmonization` does not exist.')
            for site in new_sites:
                site_gamma = pd.DataFrame(np.nan,columns=gamma_ROIs,index=[site])
                calculated_gamma = calculated_gamma.append(site_gamma)
                site_delta = pd.DataFrame(np.nan,columns=delta_ROIs,index=[site])
                calculated_delta = calculated_delta.append(site_delta)
                # populate calculated parameter table
                calculated_parameters = pd.concat([calculated_gamma,calculated_delta],axis=1).sort_index()
            gamma_ROIs = ['gamma_'+ x for x in self.datamodel.harmonization_model['ROIs']]
            delta_ROIs = ['delta_'+ x for x in self.datamodel.harmonization_model['ROIs']]
            model_gamma= pd.DataFrame(self.datamodel.harmonization_model['gamma_star'],columns=gamma_ROIs,index=[x for x in self.datamodel.harmonization_model['SITE_labels']])
            model_delta = pd.DataFrame(self.datamodel.harmonization_model['delta_star'],columns=delta_ROIs,index=[x for x in self.datamodel.harmonization_model['SITE_labels']])
            model_parameters = pd.concat([model_gamma,model_delta],axis=1).sort_index()
            parameters = pd.concat([model_parameters,calculated_parameters],axis=0).sort_index()     
            bayes_data, stand_mean = nh.harmonizationApply(self.datamodel.data[[x for x in self.datamodel.harmonization_model['ROIs']]].values,
                                                    covars,
                                                    self.datamodel.harmonization_model,True) 
            
        Raw_ROIs_Residuals = self.datamodel.data[self.datamodel.harmonization_model['ROIs']].values - stand_mean

        if 'isTrainMUSEHarmonization' in self.datamodel.data.columns:
            muse = pd.concat([self.datamodel.data['isTrainMUSEHarmonization'].reset_index(drop=True).copy(), covars, pd.DataFrame(bayes_data, columns=['H_' + s for s in self.datamodel.harmonization_model['ROIs']])],axis=1)
        else:
            muse = pd.concat([covars,pd.DataFrame(bayes_data, columns=['H_' + s for s in self.datamodel.harmonization_model['ROIs']])],axis=1)

        # harmonize derived volumes
        if ('MUSE_Volume_301' not in list(self.datamodel.harmonization_model['ROIs'])):
            logger.info('No derived volumes in model.')
            logger.info('Calculating using derived mapping dictionary.')
            MUSEDictDataFrame= self.datamodel.GetMUSEDictDataFrame()
            muse_mappings = self.datamodel.GetDerivedMUSEMap()
            for ROI in MUSEDictDataFrame[MUSEDictDataFrame['ROI_LEVEL']=='DERIVED']['ROI_INDEX']:
                single_ROIs = muse_mappings.loc[ROI].replace('NaN',np.nan).dropna().astype(np.float)
                single_ROIs = ['H_MUSE_Volume_%0d' % x for x in single_ROIs]
                muse['H_MUSE_Volume_%d' % ROI] = muse[single_ROIs].sum(axis=1,skipna=False)
            muse.drop(columns=['H_MUSE_Volume_702'], inplace=True)

        start_index = len(self.datamodel.harmonization_model['SITE_labels'])
        sex_icv_effect = np.dot(muse[['Sex','DLICV_baseline']].copy(), self.datamodel.harmonization_model['B_hat'][start_index:(start_index+2),:])
        ROIs_ICV_Sex_Residuals = ['RES_ICV_Sex_' + x for x in self.datamodel.harmonization_model['ROIs']]
        muse.loc[:,ROIs_ICV_Sex_Residuals] = muse[['H_' + x for x in self.datamodel.harmonization_model['ROIs']]].values - sex_icv_effect

        muse.loc[:,'Sex'] = muse['Sex'].map({1:'M',0:'F'})
        ROIs_Residuals = ['RES_' + x for x in self.datamodel.harmonization_model['ROIs']]
        RAW_Residuals = ['RAW_RES_' + x for x in self.datamodel.harmonization_model['ROIs']]
        muse.loc[:,ROIs_Residuals] = bayes_data-stand_mean
        muse.loc[:,RAW_Residuals] = Raw_ROIs_Residuals
        print('Harmonization done.')

        return muse, parameters