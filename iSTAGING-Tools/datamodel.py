# This Python file uses the following encoding: utf-8
"""
contact: software@cbica.upenn.edu
Copyright (c) 2018 University of Pennsylvania. All rights reserved.
Use of this source code is governed by license located in license file: https://github.com/CBICA/iSTAGING-Tools/blob/main/LICENSE
"""

import pandas as pd
import sys

class DataModel:
    """This class holds the data model."""

    def __init__(self):
        """The constructor."""
        self.data = None

    def SetData(self,d):
        """Setter"""
        self.data = d

    def GetData(self):
        """Returns complete data."""
        return self.data

    def GetData(self,roi,hue):
        """Returns a subset of data needed for plot.
        Takes as parameters the roi and hue for the plot.
        Since the plot always uses 'Age' for X axis, this is always returned."""
        d = self.data[[roi,"Age",hue]]
        return d

    def IsValid(self):
        """Checks if the data is valid or not."""

        ##TODO: Add logic to check validity of data
        ## For now, it returns True.
        return True

    def GetColumnHeaderNames(self):
        """Returns all header names for all columns in the dataset."""
        k = self.data.keys()
        return k
