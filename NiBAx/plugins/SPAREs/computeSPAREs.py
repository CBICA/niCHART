import numpy as np
import pandas as pd

#data = pd.read_pickle('/path/to/data.pkl')
#model = read_model
#SPAREModel = SPAREModelClass(data ,model)
#SPAREs = SPAREModel.getResults()

from PyQt5 import QtCore

class BrainAgeWorker(QtCore.QObject):

    done = QtCore.pyqtSignal(pd.DataFrame)
    progress = QtCore.pyqtSignal(str, int)

    #constructor
    def __init__(self, data, model):
        super(BrainAgeWorker, self).__init__()
        self.data = data
        self.model = model

    def run(self):
        print('Entering BrainAgeWorker.run() ******************************')
        y_hat = pd.DataFrame.from_dict({'SPARE_BA': np.full((self.data.shape[0],),np.nan),
                                       'SPARE_AD': np.full((self.data.shape[0],),np.nan)})

        # SPARE-BA
        idx = ~self.data[self.model['BrainAge']['predictors'][0]].isnull()

        y_hat_test = np.zeros((np.sum(idx),))
        n_ensembles = np.zeros((np.sum(idx),))

        for i,_ in enumerate(self.model['BrainAge']['scaler']):
            # Predict validation (fold) and test
            self.progress.emit('Computing SPARE-BA | Task 1 of 2', i)
            if QtCore.QThread.currentThread().isInterruptionRequested():
                self.progress.emit('Cancelled.', 0)
                self.done.emit(pd.DataFrame())
                return
            test = np.logical_not(self.data[idx]['participant_id'].isin(np.concatenate(self.model['BrainAge']['train']))) | self.data[idx]['participant_id'].isin(self.model['BrainAge']['validation'][i])
            X = self.data[idx].loc[test, self.model['BrainAge']['predictors']].values
            X = self.model['BrainAge']['scaler'][i].transform(X)
            y_hat_test[test] += (self.model['BrainAge']['svm'][i].predict(X) - self.model['BrainAge']['bias_ints'][i]) / self.model['BrainAge']['bias_slopes'][i]
            n_ensembles[test] += 1.

        y_hat_test /= n_ensembles
        y_hat.loc[idx, 'SPARE_BA'] = y_hat_test

        idx = ~self.data[self.model['AD']['predictors'][0]].isnull()

        y_hat_test = np.zeros((np.sum(idx),))
        n_ensembles = np.zeros((np.sum(idx),))

        for i,_ in enumerate(self.model['AD']['scaler']):
            # Predict validation (fold) and test
            self.progress.emit('Computing SPARE-AD | Task 2 of 2', i)
            if QtCore.QThread.currentThread().isInterruptionRequested():
                self.progress.emit('Cancelled.', 0)
                # Emit the result
                self.done.emit(pd.DataFrame())
                return
            test = np.logical_not(self.data[idx]['participant_id'].isin(np.concatenate(self.model['AD']['train']))) | self.data[idx]['participant_id'].isin(self.model['AD']['validation'][i])
            X = self.data[idx].loc[test, self.model['AD']['predictors']].values
            X = self.model['AD']['scaler'][i].transform(X)
            y_hat_test[test] += self.model['AD']['svm'][i].decision_function(X)
            n_ensembles[test] += 1. 

        y_hat_test /= n_ensembles
        y_hat.loc[idx, 'SPARE_AD'] = y_hat_test

        self.progress.emit('All done.', i)

        # Emit the result
        self.done.emit(y_hat)

class SPAREs():
    def __init__(self, data, model):
        self.data = data
        self.model = model

    def getResults(self):
        print('Entering SPAREs.getResults() ******************************')
        self.thread = QtCore.QThread()
        self.worker = BrainAgeWorker(self.datamodel.data, self.model)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.done.connect(self.thread.quit)
        self.worker.done.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        #self.worker.progress.connect(self.updateProgress)
        #self.worker.done.connect(lambda y_hat: self.OnComputationDone(y_hat))
        self.thread.start()