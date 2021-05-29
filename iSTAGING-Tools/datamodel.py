# This Python file uses the following encoding: utf-8
"""
contact: software@cbica.upenn.edu
Copyright (c) 2018 University of Pennsylvania. All rights reserved.
Use of this source code is governed by license located in license file: https://github.com/CBICA/iSTAGING-Tools/blob/main/LICENSE
"""

import pandas as pd
import sys

class DataModel:
    def __init__(self):
        self.data = None

    def SetData(self,d):
        self.data = d

    def GetData(self):
        return self.data

    def IsValid(self):
        return True

    def GetColumnHeaderNames(self):
        k = self.data.keys()
        return k
