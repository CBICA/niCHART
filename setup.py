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

if __name__ == "__main__":
  setuptools.setup(
                   packages=setuptools.find_packages(),
                   include_package_data=True,
                   package_data = {"BrainChart": ['MUSE_ROI_Dictionary.csv']},
                   long_description=readme,
                   long_description_content_type="text/markdown",
                   entry_points = {'brainchart.plugin' :
                       ['plugin1=plugins:P1', 
                        'plugin2=plugins:ScatterPlotSPAREs',
                        'plugin3=plugins:P2'],
                        'console_scripts': ['BrainChart=BrainChart:main',
                                            'QtBrainChart=QtBrainChartGUI:main']}
                  )
