import pytest
import os
import pandas as pd
from NiBAx.plugins.loadsave.dataio import DataIO
from NiBAx.plugins.spareplugin.spares import SPARE
from NiBAx.core.model.datamodel import DataModel

#This file contains tests for spares.py

#root = os.path.dirname(__file__)
#filename = os.path.join(root, 'Data','test_Pickle.pkl')

#Need spare model and data to run the test
#def test_SPARE():
#    dio = DataIO()
#    data = dio.ReadPickleFile(filename)
#    datamodel = DataModel()
#    if (data is not None) and datamodel.IsValidData(data):
#        datamodel.SetDataFilePath(filename)
#        datamodel.SetData(data)

#    sparemodel = dio.ReadSPAREModel(spare_model_file)
#    spare_instance = SPARE(datamodel,sparemodel)
#    spare_instance.DoSPAREsComputation()
#    datamodel.AddSparesToDataModel(spare_compute_instance.SPAREs)
#    dio.SavePickleFile(datamodel.data,outputfile))


