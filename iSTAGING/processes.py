# This Python file uses the following encoding: utf-8
"""
contact: software@cbica.upenn.edu
Copyright (c) 2018 University of Pennsylvania. All rights reserved.
Use of this source code is governed by license located in license file: https://github.com/CBICA/iSTAGING-Tools/blob/main/LICENSE
"""

import pandas as pd
import sys

class Processes:
    def __init__(self):
        pass

    def DoSpare(self,data):
        #TODO: implement functionality
        if (self.BrainAgeModel is None) | (self.ADModel is None):
            return data
        
        # compute SPARE-* based on saved function

        return data

    def DoHarmonization(self,data):
        #TODO: implement functionality
        pass
        #return modifieddata


