# This Python file uses the following encoding: utf-8
"""
contact: software@cbica.upenn.edu
Copyright (c) 2018 University of Pennsylvania. All rights reserved.
Use of this source code is governed by license located in license file: https://github.com/CBICA/iSTAGING-Tools/blob/main/LICENSE
"""

import pandas as pd
import numpy as np
import sys
import neuroHarmonize as nh


def predictBrainAge(data,model):
    
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


def predictAD(data,model):
    
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


class Processes:
    def __init__(self):
        pass

    def DoSPARE(self,data, ADModel, BrainAgeModel):
        print('Computing SPARE-*.')
        y_hat = predictAD(data, ADModel)
        data['SPARE_AD'] = y_hat
        y_hat = predictBrainAge(data, BrainAgeModel)
        data['SPARE_BA'] = y_hat
        print('Computing SPARE-* done.')
        return data

    def DoHarmonization(self, data, model):
        print('Running harmonization.')
        data['Sex'] = data['Sex'].map({'M':1,'F':0})
        bayes_data, stand_mean = nh.harmonizationApply(data[[x for x in model['ROIs']]].values,
                                                data[['SITE','Age','Sex','DLICV_baseline']],
                                                model,True)
        data = pd.concat([data.reset_index(), pd.DataFrame(bayes_data, columns=['H_' + s for s in model['ROIs']])],
                        axis=1)
        sex_icv_effect = np.dot(data[['Sex','DLICV_baseline']],model['B_hat'][20:22,:])
        ROIs_ICV_Sex_Residuals = ['RES_ICV_Sex_' + x for x in model['ROIs']]
        data[ROIs_ICV_Sex_Residuals] = data[['H_' + x for x in model['ROIs']]] - sex_icv_effect

        data['Sex'] = data['Sex'].map({1:'M',0:'F'})
        ROIs_Residuals = ['RES_' + x for x in model['ROIs']]
        data[ROIs_Residuals] = bayes_data-stand_mean
        print('Harmonization done.')

        return data

