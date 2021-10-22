import pandas as pd
import seaborn as sns

class P1():

    def __init__(self):
        self.name = 'Plugin 1'


    def run(self, mainwindow):
        print('Plugin P1 printout')
        if mainwindow.model.data is not None:
            print(mainwindow.model.data.shape)


class P2():

    def __init__(self):
        self.name = 'Plugin 2'


    def run(self, mainwindow):
        print('Plugin P2 printout')
        if mainwindow.model.data is not None:
            print(mainwindow.model.data.shape)



class ScatterPlotSPAREs():

    def __init__(self):
        self.name = 'Scatterplot SPARE-*'


    def run(self, mainwindow):
        if mainwindow.model.data is None:
            print("No data available.")
            return

        """Remove all plots"""
        mainwindow.plotCanvas.axes.clear()

        """Plot SPARE"""
        # clear plot
        mainwindow.plotCanvas.axes.clear()

        #get current selected combobox item
        currentROI = mainwindow.comboBoxROI.currentText()
        currentHue = mainwindow.comboBoxHue.currentText()

        # Translate ROI name back to ROI ID
        try:
            MUSEDictNAMEtoID, _ = mainwindow.model.GetMUSEDictionaries()
            if currentROI.startswith('(MUSE)'):
                currentROI = list(map(MUSEDictNAMEtoID.get, [currentROI[7:]]))[0]

            if currentROI.startswith('(Harmonized MUSE)'):
                currentROI = 'H_' + list(map(MUSEDictNAMEtoID.get, [currentROI[18:]]))[0]

            if currentROI.startswith('(Residuals MUSE)'):
                currentROI = 'RES_' + list(map(MUSEDictNAMEtoID.get, [currentROI[17:]]))[0]

            if currentROI.startswith('(WMLS)'):
                currentROI = list(map(MUSEDictNAMEtoID.get, [currentROI[7:]]))[0].replace('MUSE_', 'WMLS_')
        except:
            currentROI = 'DLICV'
            self.comboBoxROI.setCurrentText('DLICV')
            print("Could not translate combo box item. Setting to `DLICV`.")

        #create empty dictionary of plot options
        plotOptions = dict()

        #fill dictionary with options
        plotOptions['ROI'] = currentROI
        plotOptions['HUE'] = currentHue

        # set hue
        currentHue = plotOptions['HUE']

        if not currentHue:
            currentHue = 'Sex'

        # seaborn plot on axis
        if (('SPARE_AD' in mainwindow.model.GetColumnHeaderNames()) &
            ('SPARE_BA' in mainwindow.model.GetColumnHeaderNames())):
            spare_data = mainwindow.model.GetData(['SPARE_BA','SPARE_AD'],
                                           currentHue).copy()
            spare_data.loc[:, 'SPARE_BA'] = spare_data['SPARE_BA'] - spare_data['Age'] 
            sns.scatterplot(x='SPARE_AD', y='SPARE_BA', hue=currentHue,ax=mainwindow.plotCanvas.axes,
                            s=5, data=spare_data)
        else:
            # Set error text on plot
            mainwindow.plotCanvas.axes.text(0.5,0.5,'No SPARE-* scores available.',
                           va='center', ha='center')
            print('Plotting failed. Check data set for inclusion of SPARE-* indices.')

        # refresh canvas
        mainwindow.plotCanvas.draw()