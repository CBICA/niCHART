# This Python file uses the following encoding: utf-8
"""
contact: software@cbica.upenn.edu
Copyright (c) 2018 University of Pennsylvania. All rights reserved.
Use of this source code is governed by license located in license file: https://github.com/CBICA/BrainChart/blob/main/LICENSE
"""

from PyQt5 import QtCore, QtGui, QtWidgets
import argparse
import os, sys
from NiBAx.mainwindow import MainWindow

def main():
    parser = argparse.ArgumentParser(description='iSTAGING Data Visualization and Preparation')
    parser.add_argument('--data_file', type=str, help='Data file containing data frame.', default=None, required=False)
    parser.add_argument('--harmonization_model_file', type=str, help='Harmonization model file.', default=None, required=False)
    parser.add_argument('--SPARE_model_file', type=str, help='Model file for SPARE-scores.', default=None, required=False)

    args = parser.parse_args(sys.argv[1:])

    data_file = args.data_file
    harmonization_model_file = args.harmonization_model_file
    SPARE_model_file = args.SPARE_model_file

    app = QtWidgets.QApplication(sys.argv)
    mw = MainWindow(dataFile=data_file,
                    harmonizationModelFile=harmonization_model_file,
                    SPAREModelFile=SPARE_model_file)
    mw.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
