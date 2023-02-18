import pandas as pd
import numpy as np
import sklearn.decomposition
from sklearn.decomposition import PCA
from sys import argv
from sklearn.preprocessing import StandardScaler
from joblib import dump
from joblib import load
import muse_qc

# test on v1.1/istaging.pkl.gz MUSE ROIs
data = pd.read_pickle("istaging.pkl.gz")
data_notnull=data[data.MUSE_Volume_702.notna()]
data_nutnull_muse = data_notnull.loc[:, 'MUSE_Volume_702':'MUSE_Volume_207']
data_nutnull_muse.reset_index(inplace=True,drop=True)
data_nutnull_muse.shape

# randomly split data into test and reference
reference=data_nutnull_muse.sample(frac=0.6,random_state=200) #random state is a seed value
test=data_nutnull_muse.drop(reference.index)

#convert to numpy array
roi_data_prepare_np = test.to_numpy()
ref_data_prepare_np = reference.to_numpy()

#get MHD results, reference-based scaler and reference-based PCA model by providing test ROIs and reference ROIs 
res, ref_scaler, ref_model = muse_qc.getMHD_from_RefROIs(roi_data_prepare_np, ref_data_prepare_np,3)

#save reference-based scaler and reference-based model
dump(ref_scaler, 'ref_based_scaler.joblib')
dump(ref_model, 'ref_based_PCA_model.joblib')

#load reference-based scaler and reference-based model
ref_scaler = load('ref_based_scaler.joblib')
ref_model = load('ref_based_PCA_model.joblib')

#get MHD results by providing test ROIs, reference-based scaler and reference-based PCA model 
res2 = muse_qc.getMHD_from_RefModel(roi_data_prepare_np, ref_scaler,ref_model,3)



