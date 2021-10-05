# This Python file uses the following encoding: utf-8
"""
contact: software@cbica.upenn.edu
Copyright (c) 2018 University of Pennsylvania. All rights reserved.
Use of this source code is governed by license located in license file: https://github.com/CBICA/BrainChart/blob/main/LICENSE
"""

import pandas as pd
import joblib
import os, sys

class DataIO:
    def __init__(self):
        pass


    def ReadPickleFile(self,filename):
        data = pd.read_pickle(filename)
        return data


    def SavePickleFile(self,data,filename):
        data.to_pickle(filename)

    def ReadMUSEDictionary(salf):
        # Load MUSE dictionary file
        MUSEDict = os.path.join(os.path.dirname(__file__), 'MUSE_ROI_Dictionary.csv')
        MUSEDict = pd.read_csv(MUSEDict)

        # Create lookup from name to ID and vice-versa
        # e.g. name to ID: Hippocampus right -> MUSE_Volume_48
        MUSEDictNAMEtoID = dict(zip(MUSEDict['ROI_NAME'], MUSEDict['ROI_COL']))
        # e.g. ID to name; MUSE_Volume_48 -> Hippocampus right
        MUSEDictIDtoNAME = dict(zip(MUSEDict['ROI_COL'], MUSEDict['ROI_NAME']))

        return MUSEDictNAMEtoID, MUSEDictIDtoNAME

        
    def ReadSPAREModel(self, filename):
        with open(filename, "rb") as file:
            BrainAgeModel, ADModel = joblib.load(filename)
        
        return BrainAgeModel, ADModel
