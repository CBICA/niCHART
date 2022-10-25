# This Python file uses the following encoding: utf-8
"""
contact: software@cbica.upenn.edu
Copyright (c) 2018 University of Pennsylvania. All rights reserved.
Use of this source code is governed by license located in license file: https://github.com/CBICA/NiBAx/blob/main/LICENSE
"""

from PyQt5 import QtCore, QtGui, QtWidgets
import os
import pandas as pd
from NiBAx.plugins.loadsave.dataio import DataIO
from NiBAx.plugins.sparesplugin.spares import SPARE, BrainAgeWorker
from NiBAx.plugins.harmonizationplugin.harmonization import Harmonize
from NiBAx.core.model.datamodel import DataModel

class NiBAxCmdApp:
    def __init__(self):
        self.dio = DataIO()
        self.datamodel = DataModel()

    def LoadData(self, datafile):
        print("Reading data")
        data = self.dio.ReadPickleFile(datafile)

        #also read MUSE dictionary
        MUSEDictNAMEtoID, MUSEDictIDtoNAME, MUSEDictDataFrame = self.dio.ReadMUSEDictionary()
        self.datamodel.SetMUSEDictionaries(MUSEDictNAMEtoID, MUSEDictIDtoNAME,MUSEDictDataFrame)

        #also read Derived MUSE dictionary 
        DerivedMUSEMap = self.dio.ReadDerivedMUSEMap()
        self.datamodel.SetDerivedMUSEMap(DerivedMUSEMap)

        #set data into datamodel
        if (data is not None) and self.datamodel.IsValidData(data):
            self.datamodel.SetDataFilePath(datafile)
            self.datamodel.SetData(data)

        return self


    def Harmonize(self, harmonizationmodelfile,outputfile):

        print("Reading harmonization model")
        harmonizationmodel = self.dio.ReadPickleFile(harmonizationmodelfile)

        print("Harmonizing MUSE ROIs")
        harmonized_rois = Harmonize(self.datamodel,harmonizationmodel)
        muse, parameters = harmonized_rois.DoHarmonization()

        print('Adding residuals and harmonized volumes to data frame...')
        harmonized_rois.AddHarmonizedMUSE(muse)

        print("Saving updated data at specified location")
        self.dio.SavePickleFile(self.datamodel.data,outputfile)

        print("Done")
        return self

    def ComputeSpares(self, sparesmodelfile, outputfile):

        print("reading spare model")
        sparemodel = {'BrainAge': None, 'AD': None}
        sparemodel['BrainAge'], sparemodel['AD'] = self.dio.ReadSPAREModel(sparesmodelfile)

        print("computing SPARE scores")
        spare_compute_instance = SPARE(self.datamodel,sparemodel)
        spare_compute_instance.DoSPAREsComputation()

        print('Adding SPARE-* scores to data frame...')
        self.datamodel.AddSparesToDataModel(spare_compute_instance.SPAREs)

        print("saving updated data at specified location")
        self.dio.SavePickleFile(self.datamodel.data,outputfile)

        print("Done")
        return self


if __name__ == '__main__':
    pass
