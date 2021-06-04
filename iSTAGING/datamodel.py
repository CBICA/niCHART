# This Python file uses the following encoding: utf-8
"""
contact: software@cbica.upenn.edu
Copyright (c) 2018 University of Pennsylvania. All rights reserved.
Use of this source code is governed by license located in license file: https://github.com/CBICA/iSTAGING-Tools/blob/main/LICENSE
"""

import pandas as pd
import numpy as np
from iSTAGING.dataio import DataIO
import neuroHarmonize as nh
import importlib.resources as pkg_resources
import sys


class DataModel:
    """This class holds the data model."""

    def __init__(self,DataFile=None,HarmonizationModelFile=None):
        """The constructor."""
        if DataFile is None:
            self.data = None
        else:
            dio = DataIO()
            d = dio.ReadPickleFile(DataFile)
            self.SetData(d)

        if HarmonizationModelFile is None:
            self.harmonization_model = None
        else:
            dio = DataIO()
            m = dio.ReadPickleFile(HarmonizationModelFile)
            self.SetHarmonizationModel(m)
        
    def SetData(self,d):
        """Setter"""
        self.data = d

    def SetHarmonizationModel(self,m):
        """Setter"""
        self.harmonization_model = m

    def GetData(self):
        """Returns complete data."""
        return self.data

    def GetModel(self):
        """Returns harmonization model."""
        return self.harmonization_model

    def GetNormativeRange(self,roi):
        """Return normative range"""
        
        # Constructig the visualization of the normative range based on GAM
        # model
        covariates = pd.DataFrame(np.linspace(25, 95, 200), columns=['Age'])
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
        d = self.data[[roi,"Age",hue]]
        return d

    def IsValid(self):
        """Checks if the data is valid or not."""
        if not isinstance(self.data, pd.DataFrame):
            return False
        if 'participant_id' not in self.data.columns:
            return False
        elif 'Age' not in self.data.columns:
            return False
        elif 'Sex' not in self.data.columns:
            return False
        else:
            return True


    def GetColumnHeaderNames(self):
        """Returns all header names for all columns in the dataset."""
        k = self.data.keys()
        return k

    def Reset(self):
        #clear all contents of data/empty memory etc.
        #TODO: this needs to be done correctly,
        #Is there a better way to clear data?
        del self.data
        del self.harmonization_model
        self.harmonization_model = None
        self.data = None
