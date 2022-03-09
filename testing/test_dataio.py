import pytest
import os
import pandas as pd
from NiBAx.plugins.loadsave.dataio import DataIO

#This file contains tests for dataio.py

root = os.path.dirname(__file__)
filename = os.path.join(root, 'Data','test_Pickle.pkl')

data = [{'A': 10, 'B': 20, 'C':30}, {'x':100, 'y': 200, 'z': 300},{'x':0.34, 'y': 1.5, 'z': 1000.3503},{'A': -100, 'B': -0.20, 'C':310}]

def test_ReadPickleFile():
    #instantiate our class to be tested and read pkl file
    dio = DataIO()
    df = dio.ReadPickleFile(filename)

    #read expected data
    expecteddf = pd.DataFrame(data)

    #compare read data with expected data
    assert df.equals(expecteddf)

def test_SavePickleFile(tmpdir):
    #read sample data
    testdf =pd.DataFrame(data)

    #create output path to tmpdir location
    outputPath = os.path.join(tmpdir,"written_data.pkl")
#   print("outputPath: ", outputPath)

    #instantiate our class to be tested and write pkl file
    dio = DataIO()
    dio.SavePickleFile(testdf,os.path.join(tmpdir,"written_data.pkl"))

    #read written file
    df = pd.read_pickle(outputPath)

    #compare with expected data
    assert df.equals(testdf)

def test_ReadMUSEDictionary():
    print("Need test dataset to run this test")
    assert False

def test_ReadSPAREModel():
    print("Need test dataset to run this test")
    assert False
