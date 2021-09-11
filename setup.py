import setuptools

setuptools.setup( name="iSTAGING",
                  version="0.0.1",
                  packages=setuptools.find_packages(),
                  include_package_data=True,
                  package_data = {"iSTAGING": ['MUSE_ROI_Dictionary.csv']},
                  )
