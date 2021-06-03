# This Python file uses the following encoding: utf-8
"""
contact: software@cbica.upenn.edu
Copyright (c) 2018 University of Pennsylvania. All rights reserved.
Use of this source code is governed by license located in license file: https://github.com/CBICA/iSTAGING-Tools/blob/main/LICENSE
"""

import pandas as pd
import sys

class DataIO:
    def __init__(self):
        pass

    def ReadPickleFile(self,filename):
        data = pd.read_pickle(filename)
        return data


