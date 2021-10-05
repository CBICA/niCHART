import setuptools

if __name__ == "__main__":
  setuptools.setup(
                   packages=setuptools.find_packages(),
                   include_package_data=True,
                   package_data = {"BrainChart": ['MUSE_ROI_Dictionary.csv']},
                  )
