# This Python file uses the following encoding: utf-8
"""
contact: software@cbica.upenn.edu
Copyright (c) 2018 University of Pennsylvania. All rights reserved.
Use of this source code is governed by license located in license file: https://github.com/CBICA/BrainChart/blob/main/LICENSE
"""

import pandas as pd
import numpy as np
import sys
import neuroHarmonize as nh


class Processes:
    def __init__(self):
        pass

    def predictBrainAge(self, data, model):
        
        idx = ~data[model['predictors'][0]].isnull()

        y_hat_test = np.zeros((np.sum(idx),))
        n_ensembles = np.zeros((np.sum(idx),))

        for i,_ in enumerate(model['scaler']):
            print('SPARE-BA fold %d' % (i))
            # Predict validation (fold) and test
            test = np.logical_not(data[idx]['participant_id'].isin(np.concatenate(model['train']))) | data[idx]['participant_id'].isin(model['validation'][i])
            X = data[idx].loc[test, model['predictors']].values
            X = model['scaler'][i].transform(X)
            y_hat_test[test] += (model['svm'][i].predict(X) - model['bias_ints'][i]) / model['bias_slopes'][i]
            n_ensembles[test] += 1.

        y_hat_test /= n_ensembles
        y_hat = np.full((data.shape[0],),np.nan)
        y_hat[idx] = y_hat_test

        return y_hat


    def predictAD(self, data, model):
        
        idx = ~data[model['predictors'][0]].isnull()

        y_hat_test = np.zeros((np.sum(idx),))
        n_ensembles = np.zeros((np.sum(idx),))

        for i,_ in enumerate(model['scaler']):
            print('SPARE-AD fold %d' % (i))
            # Predict validation (fold) and test
            test = np.logical_not(data[idx]['participant_id'].isin(np.concatenate(model['train']))) | data[idx]['participant_id'].isin(model['validation'][i])
            X = data[idx].loc[test, model['predictors']].values
            X = model['scaler'][i].transform(X)
            y_hat_test[test] += model['svm'][i].decision_function(X)
            n_ensembles[test] += 1.

        y_hat_test /= n_ensembles
        y_hat = np.full((data.shape[0],),np.nan)
        y_hat[idx] = y_hat_test

        return y_hat


    def DoSPARE(self,data, ADModel, BrainAgeModel):
        print('Computing SPARE-*.')
        y_hat = self.predictAD(data, ADModel)
        data['SPARE_AD'] = y_hat
        y_hat = self.predictBrainAge(data, BrainAgeModel)
        data['SPARE_BA'] = y_hat
        print('Computing SPARE-* done.')
        return data


    def DoHarmonization(self, data, model):
        print('Running harmonization.')


        data['Sex'] = data['Sex'].map({'M':1,'F':0})
        bayes_data, stand_mean = nh.harmonizationApply(data[[x for x in model['ROIs']]].values,
                                                data[['SITE','Age','Sex','DLICV_baseline']],
                                                model,True)

        Raw_ROIs_Residuals = data[model['ROIs']].values - stand_mean

        # create list of new SITEs to loop through
        new_sites = set(data['SITE'].value_counts().index.tolist())^set(model['SITE_labels'])

        var_pooled = model['var_pooled']

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


        if ('H_MUSE_Volume_47' not in data.keys()):
            data = pd.concat([data.reset_index(), pd.DataFrame(bayes_data, columns=['H_' + s for s in model['ROIs']])],
                            axis=1)    
        start_index = len(model['SITE_labels'])
        sex_icv_effect = np.dot(data[['Sex','DLICV_baseline']],model['B_hat'][start_index:(start_index+2),:])
        ROIs_ICV_Sex_Residuals = ['RES_ICV_Sex_' + x for x in model['ROIs']]
        data[ROIs_ICV_Sex_Residuals] = data[['H_' + x for x in model['ROIs']]] - sex_icv_effect

        data['Sex'] = data['Sex'].map({1:'M',0:'F'})
        ROIs_Residuals = ['RES_' + x for x in model['ROIs']]
        data[ROIs_Residuals] = bayes_data-stand_mean
        print('Harmonization done.')

        return data

