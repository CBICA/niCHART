# This Python file uses the following encoding: utf-8
"""
contact: software@cbica.upenn.edu
Copyright (c) 2018 University of Pennsylvania. All rights reserved.
Use of this source code is governed by license located in license file: https://github.com/CBICA/NiBAx/blob/main/LICENSE
"""

from PyQt5 import QtCore, QtGui, QtWidgets
import argparse
import os, sys
from NiBAx.mainwindow import MainWindow
from NiBAx.NiBAxCmdApp import NiBAxCmdApp

def main():
    parser = argparse.ArgumentParser(description='NiBAx Data Visualization and Preparation')
    parser.add_argument('--data_file', type=str, help='Data file containing data frame.', default=None, required=False)
    parser.add_argument('--MUSE_harmonization_model_file', type=str, help='MUSE Harmonization model file.', default=None, required=False)
    parser.add_argument('--SPARE_model_file', type=str, help='Model file for SPARE-scores.', default=None, required=False)
    parser.add_argument('-harmonize', action="store_true", help='Do harmonization if flag is set[ignored currently].')
    parser.add_argument('-compute_spares', action="store_true", help='Compute SPARE-scores if flag is set.')
    parser.add_argument('--output_file_name', type=str, help='Name of the output file with extension.', default=None, required=False)
    parser.add_argument("-nogui", action="store_true", help="Launch application in CLI mode to do data processing without any visualization or graphical user interface.")

    args = parser.parse_args(sys.argv[1:])

    data_file = args.data_file
    MUSE_harmonization_model_file = args.MUSE_harmonization_model_file
    SPARE_model_file = args.SPARE_model_file
    harmonize = args.harmonize
    compute_spares = args.compute_spares
    output_file = args.output_file_name
    noGUI = args.nogui

    if(noGUI):
        app = QtCore.QCoreApplication(sys.argv)
        if(harmonize):
            if((data_file == None) or (MUSE_harmonization_model_file == None) or (output_file == None)):
                print("Please provide '--data_file', '--harmonization_model_file' and optionally '--output_file_name' to compute harmonized volumes.")
                exit()
            App = NiBAxCmdApp()
            App.LoadData(data_file).Harmonize(MUSE_harmonization_model_file, output_file)
        if(compute_spares):
            if((data_file == None) or (SPARE_model_file == None) or (output_file == None)):
                print("Please provide '--data_file', '--MUSE_harmonization_model_file', '--SPARE_model_file' and optionally '--output_file_name' to compute spares.")
                exit()
            NiBAxCmdApp().LoadData(data_file).Harmonize(MUSE_harmonization_model_file, output_file).ComputeSpares(SPARE_model_file, output_file)
    
    else:
        app = QtWidgets.QApplication(sys.argv)
        mw = MainWindow(dataFile=data_file,
                        harmonizationModelFile=MUSE_harmonization_model_file,
                        SPAREModelFile=SPARE_model_file)
        mw.show()

        sys.exit(app.exec_())

if __name__ == '__main__':
    main()
