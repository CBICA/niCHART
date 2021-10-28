#!/usr/bin/env python

"""The setup script."""

import setuptools, sys, re

with open("README.md") as readme_file:
    readme = readme_file.read()


try:
    filepath = "BrainChart/version.py"
    version_file = open(filepath)
    (__version__,) = re.findall('__version__ = "(.*)"', version_file.read())

except Exception as error:
    __version__ = "0.0.0"
    sys.stderr.write("Warning: Could not open '%s' due %s\n" % (filepath, error))


# Requirements
requirements = ['cycler==0.10.0',
                'joblib==1.0.1',
                'kiwisolver==1.3.1',
                'matplotlib==3.4.2',
                'nibabel==3.2.1',
                'numpy==1.20.3',
                'neuroHarmonize==2.1',
                'pandas==1.3.4',
                'Pillow==8.2.0',
                'pyparsing==2.4.7',
                'PyQt5==5.15.4',
                'PyQt5_Qt5==5.15.2',
                'PyQt5_sip==12.9.0',
                'dill==0.3.4',
                'future==0.18.2',
                'python_dateutil==2.8.1',
                'pytz==2021.1',
                'scikit_learn==0.24.2',
                'scipy==1.6.3',
                'seaborn==0.11.1',
                'six==1.16.0',
                'statsmodels==0.13.0']

if __name__ == "__main__":
  setuptools.setup(
                   packages=setuptools.find_packages(),
                   include_package_data=True,
                   package_data = {"BrainChart": ['MUSE_ROI_Dictionary.csv']},
                   install_requires = requirements,
                   long_description=readme,
                   long_description_content_type="text/markdown",
                   entry_points = {'brainchart.plugin' :
                       ['plugin1=plugins:P1', 
                        'plugin2=plugins:ScatterPlotSPAREs',
                        'plugin3=plugins:P2',
                        'plugin4=plugins:ScatterPlotMUSE'],
                        'console_scripts': ['BrainChart=BrainChart:main']}
                  )
