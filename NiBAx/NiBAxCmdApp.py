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
from NiBAx.plugins.harmonizationplugin.harmonization import harmonize
from NiBAx.core.model.datamodel import DataModel

class NiBAxCmdApp:
    def __init__(self):
        pass

    def harmonize(self,datafile,harmonizationmodelfile,outputfile):
        print("reading data")
        dio = DataIO()
        data = dio.ReadPickleFile(datafile)

        #set data into datamodel
        datamodel = DataModel()
        if (data is not None) and datamodel.IsValidData(data):
            datamodel.SetDataFilePath(datafile)
            datamodel.SetData(data)

        print("reading harmonization model")
        harmonizationmodel = dio.ReadPickleFile(harmonizationmodelfile)

        print("harmonizing MUSE ROIs")
        harmonized_rois = harmonize(datamodel,harmonizationmodel)
        harmonized_rois.Doharmonization()

        print('Adding residuals and harmonized volumes to data frame...')
        datamodel.AddHarmonizedVolumes(harmonized_rois.SPAREs)

        print("saving updated data at specified location")
        dio.SavePickleFile(datamodel.data,outputfile)

        print("Done")

    def ComputeSpares(self,datafile,sparesmodelfile,outputfile):
        print("reading data")
        dio = DataIO()
        data = dio.ReadPickleFile(datafile)

        #set data into datamodel
        datamodel = DataModel()
        if (data is not None) and datamodel.IsValidData(data):
            datamodel.SetDataFilePath(datafile)
            datamodel.SetData(data)

        print("reading spare model")
        sparemodel = {'BrainAge': None, 'AD': None}
        sparemodel['BrainAge'], sparemodel['AD'] = dio.ReadSPAREModel(sparesmodelfile)

        print("computing SPARE scores")
        spare_compute_instance = SPARE(datamodel,sparemodel)
        spare_compute_instance.DoSPAREsComputation()

        print('Adding SPARE-* scores to data frame...')
        datamodel.AddSparesToDataModel(spare_compute_instance.SPAREs)

        print("saving updated data at specified location")
        dio.SavePickleFile(datamodel.data,outputfile)

        print("Done")


if __name__ == '__main__':
    main()
