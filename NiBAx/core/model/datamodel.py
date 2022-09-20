# This Python file uses the following encoding: utf-8
"""
contact: software@cbica.upenn.edu
Copyright (c) 2018 University of Pennsylvania. All rights reserved.
Use of this source code is governed by license located in license file: https://github.com/CBICA/NiBAx/blob/main/LICENSE
"""

import pandas as pd
import numpy as np
import neuroHarmonize as nh
import importlib.resources as pkg_resources
import sys
import joblib
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5 import QtCore
from NiBAx.core import iStagingLogger

logger = iStagingLogger.get_logger(__name__)

class DataModel(QObject):
    """This class holds the data model."""

    data_changed = QtCore.pyqtSignal()

    def __init__(self):
        QObject.__init__(self)
        """The constructor."""
        self.data = None
        self.harmonization_model = None
        self.MUSEDictNAMEtoID = None
        self.MUSEDictIDtoNAME = None
        self.data_FilePath = None
        self.harmonization_model_Filepath = None
        self.SPAREModel = None
        self.BrainAgeModel = None
        self.ADModel = None


    def SetMUSEDictionaries(self, MUSEDictNAMEtoID, MUSEDictIDtoNAME,MUSEDictDataFrame):
        """Setter for MUSE dictionary"""
        self.MUSEDictNAMEtoID = MUSEDictNAMEtoID
        self.MUSEDictIDtoNAME = MUSEDictIDtoNAME
        self.MUSEDictDataFrame = MUSEDictDataFrame
    
    def SetDerivedMUSEMap(self,DerivedMUSEMap):
        """Setter for Derived MUSE dictionary"""
        self.DerivedMUSEMap = DerivedMUSEMap


    def SetDataFilePath(self,p):
        """Setter"""
        self.data_FilePath = p


    def SetHarmonizationModelFilePath(self,p):
        """Setter"""
        self.harmonization_model_Filepath = p


    def GetDataFilePath(self):
        """Return data file path"""
        return self.data_FilePath


    def GetHarmonizationModelFilePath(self):
        """Return harmonization model file path"""
        return self.harmonization_model_Filepath


    def GetMUSEDictionaries(self):
        """Get the MUSE dictionaries to map from ID to name and vice-versa"""
        return self.MUSEDictNAMEtoID, self.MUSEDictIDtoNAME
    
    def GetDerivedMUSEMap(self):
        """Get the derived MUSE dictionary to map from SINGLE to DERIVED ROIs"""
        return self.DerivedMUSEMap
    
    def GetMUSEDictDataFrame(self):
        """Get the MUSE dictionaries to map from ID to name and vice-versa"""
        return self.MUSEDictDataFrame

        
    def SetData(self,d):
        """Setter for data"""
        self.data = d
        logger.info('Data changed in datamodel. Signal emitted.')
        self.data_changed.emit()


    def SetHarmonizationModel(self,m):
        """Setter for neuroHarmonize model"""
        self.harmonization_model = m
        logger.info('neuroHarmonize model set.')


    def SetSPAREModel(self,BrainAgeModel, ADModel):
        """Setter for SPARE-* models"""
        print('setting SPARE models')
        self.BrainAgeModel = BrainAgeModel
        self.ADModel = ADModel


    def GetCompleteData(self):
        """Returns complete data."""
        return self.data


    def GetModel(self):
        """Returns harmonization model."""
        return self.harmonization_model
    
    def GetMaxAgeOfMUSEHarmonizationModel(self):
        """Returns model age maximum."""
        return self.harmonization_model['smooth_model']['bsplines_constructor'].knot_kwds[0]['upper_bound']

    def GetMinAgeOfMUSEHarmonizationModel(self):
        """Returns model age minimum."""
        return self.harmonization_model['smooth_model']['bsplines_constructor'].knot_kwds[0]['lower_bound']
        

    def GetNormativeRange(self,roi):
        """Return normative range"""
        
        # Constructig the visualization of the normative range based on GAM
        # model
        covariates = pd.DataFrame(np.linspace(self.GetMinAgeOfMUSEHarmonizationModel(), self.GetMaxAgeOfMUSEHarmonizationModel(), 200), columns=['Age'])
        # Fix ICV roughly to population average
        covariates['ICV'] = 1450000 # mean ICV
        # Fix Sex variable
        covariates['Sex'] = 0
        # No need to specify site, but column with name `SITE` must exist
        covariates['SITE'] = 'None'
        # Set the ROI to be predicted
        ROIs = self.harmonization_model['ROIs']
        # Compute predicted mean for specific ROI
        # TODO: This is inefficient because the mean values are predicted for
        #       all ROIs every time. Computation is only necessary if the
        #       covariates change (e.g. for different `Sex`).
        _, stand_mean = nh.harmonizationApply(np.full((covariates.shape[0], len(ROIs)), np.nan),
                                              covariates[['SITE','Age','Sex','ICV']],
                                              self.harmonization_model, True)
        y = stand_mean[:,ROIs.index(roi)]
        # Get the normative range based on pooled variance
        z = 2.*np.sqrt(self.harmonization_model['var_pooled'][ROIs.index(roi)])
        # Return age and associated mean value as well as normative range
        return covariates['Age'], y, z


    def GetData(self,roi,hue):
        """Returns a subset of data needed for plot.
        Takes as parameters the roi and hue for the plot.
        Since the plot always uses 'Age' for X axis, this is always returned."""
        if not isinstance(roi, list):
            roi = [roi]
        
        d = self.data[roi + ["Age",hue]]
        return d


    def IsValidData(self, data=None):
        """Checks if the data is valid or not."""
        if data is None:
            data = self.data
        
        if not isinstance(data, pd.DataFrame):
            return False
        if 'participant_id' not in data.columns:
            return False
        elif 'Age' not in data.columns:
            return False
        elif 'Sex' not in data.columns:
            return False
        else:
            return True


    def IsValidHarmonization(self):
        """Checks if the harmonization model is valid or not."""
        #TODO: Implement checks
        return True


    def IsValidSPARE(self):
        """Checks if the SPARE-* model is valid or not."""
        #TODO: Implement checks
        return True


    def GetColumnHeaderNames(self):
        """Returns all header names for all columns in the dataset."""
        if self.data is not None:
            k = self.data.keys()
        else:
            k = []
        
        return k


    def GetColumnDataTypes(self):
        """Returns all header names for all columns in the dataset."""
        d = self.data.dtypes
        return d
    

    def Reset(self):
        #clear all contents of data/model and release memory etc.
        #TODO: this needs to be done correctly,
        #is there a better way to clear data?
        del self.data
        del self.harmonization_model
        self.harmonization_model = None
        self.data = None

    def GetDataStatistics(self):
        """Returns a dictionary of data statistics.
        Currently returned stats:
        # Observation,
        # Participants
        # Age [min,max]
        # Sex [M,F]"""

        #create empty dictionary
        stats = dict()

        #fill dictionary with data stats
        stats['minAge'] = self.data['Age'].min()
        stats['maxAge'] = self.data['Age'].max()
        stats['meanAge'] = self.data['Age'].mean()
        stats['numParticipants'] = len(self.data['participant_id'].unique())
        stats['numObservations'] = self.data.shape[0]

        sex = self.data[['participant_id','Sex']].drop_duplicates()
        sex['Sex'] = sex['Sex'].astype('category')
        sex['Sex'] = sex['Sex'].cat.set_categories(['M', 'F'])
        stats['countsPerSex'] = sex['Sex'].value_counts()

        return stats

    def AddSparesToDataModel(self,spares,SPARE_AD='SPARE_AD',
                             SPARE_BA='SPARE_BA'):
        self.data.loc[:,SPARE_AD] = spares['SPARE_AD']
        self.data.loc[:,SPARE_BA] = spares['SPARE_BA']
        self.data_changed.emit()
