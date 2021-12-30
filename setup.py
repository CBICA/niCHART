#!/usr/bin/env python

"""The setup script."""

import setuptools, sys, re

with open("README.md") as readme_file:
    readme = readme_file.read()


if __name__ == "__main__":
  setuptools.setup(
                   packages=setuptools.find_packages(),
                   include_package_data=True,
                   long_description=readme,
                   long_description_content_type="text/markdown",
                   entry_points = {
                        'console_scripts': ['NiBAx=NiBAx:main']}
                  )
