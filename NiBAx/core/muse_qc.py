import pandas as pd
import numpy as np
import sklearn.decomposition
from sklearn.decomposition import PCA
from sys import argv
from sklearn.preprocessing import StandardScaler

def getMHD_from_RefROIs(ROIs, ROIsReference, n_components=3):
    
    '''
    Usage Information
    
    ROIs: pandas dataframe or numpy array with numeric values
    
    ROIsReference: numpy array with numeric values (will be used to calculate scaler and PCA)
    
    Returns: MHD result, reference-based scaler and reference-based PCA model
    
    '''
    
    # check ROIs's type; if dataframe, convert to numpy array; if numpy array, continue; if else, exit
    if isinstance(ROIs, pd.DataFrame):
        ROIs = ROIs.to_numpy()
    elif isinstance(ROIs, np.ndarray):
        pass
    else:
        print("Please check input ROIs file type! Expecting pandas dataframe or numpy array!")
        exit(1)
        
    # check if ROIs is numeric; will get error if can't be converted to numeric
    ROIs = ROIs.astype(float)
    
    # check if the number of columns is larger than n_components
    n_col = ROIs.shape[1]
    if n_col <= n_components:
        print("Please make sure the number of columns is larger than n_components !")
        exit(1)
        
    # check if ROIsReference is a numpy array; if yes, then compute PCA object using ROIsRefenece as data and apply model on ROIs; if is a PCA object, apply model on ROIs
    if isinstance(ROIsReference, np.ndarray): 
        
        if ROIsReference.shape[1] > n_components:
            # standardize ROIsReference and fit the model
            scaler = StandardScaler()
            ROIsReference_S = scaler.fit_transform(ROIsReference) 
            
            pca = PCA(n_components = n_components,svd_solver='randomized',random_state=100)
            pca_ref = pca.fit(ROIsReference_S)
            
            # standardize ROIs and apply model 
            ROIs_S = scaler.transform(ROIs)
            ROIs_transformed = pca_ref.transform(ROIs_S)
            
        else:
            print("Please check your ROIsReference!")
            exit(1)
        
    else:
        print("Please check your ROIsReference file type!")
        exit(1)
        
        
    # calculateMahalanobis
    result = getMahalanobis(ROIs_transformed)
    

    # return values, ref-based scaler and ref-based model 
    return result, scaler, pca_ref
    
 
def getMHD_from_RefModel(ROIs, ReferenceScaler, ReferenceModel, n_components=3):
    
    '''
    Usage Information
    
    ROIs: pandas dataframe or numpy array with numeric values
    
    ReferenceScaler: scaler object
    
    ReferenceModel: PCA object (numpy array) with column number equals to n_components
    
    Returns: MHD result
    '''
    
    # check ROIs's type; if dataframe, convert to numpy array; if numpy array, continue; if else, exit
    if isinstance(ROIs, pd.DataFrame):
        ROIs = ROIs.to_numpy()
    elif isinstance(ROIs, np.ndarray):
        pass
    else:
        print("Please check input ROIs file type! Expecting pandas dataframe or numpy array!")
        exit(1)
        
    # check if ROIs is numeric; will get error if can't be converted to numeric
    ROIs = ROIs.astype(float)
    
    # check if the number of columns is larger than n_components
    n_col = ROIs.shape[1]
    if n_col <= n_components:
        print("Please make sure the number of columns is larger than n_components !")
        exit(1)
        
    # check if ReferenceScaler is correct type 
    if isinstance(ReferenceScaler,sklearn.preprocessing._data.StandardScaler) is False: 
        print("Please check your ReferenceScaler!")
        exit(1)
            
    # check if ReferenceModel is correct type 
    if isinstance(ReferenceModel,sklearn.decomposition._pca.PCA) is False: 
        print("Please check your ReferenceModel!")
        exit(1)

    # standardize ROIs and apply model 
    ROIs_S = ReferenceScaler.fit_transform(ROIs)
    ROIs_transformed = ReferenceModel.transform(ROIs_S)
 
        
    # calculateMahalanobis
    result = getMahalanobis(ROIs_transformed)
    

    # return values 
    return result
    
def getMahalanobis(ROIs_transformed):
    import scipy as sp
    from scipy.spatial.distance import mahalanobis
    
    # removing subjects with inf values
    ROIs_transformed_red = ROIs_transformed[np.where((ROIs_transformed.mean(axis=1) != np.inf) & (ROIs_transformed.mean(axis=1) != np.nan))[0],:]

    # calculate mean values of the roi values
    ROIs_transformed_mean = ROIs_transformed_red.mean(axis=0 )
 
    # calculate inverse of the covariance matrix
    VI = sp.linalg.inv( np.cov(ROIs_transformed_red, rowvar=False))

    # calculate squared mahalanobis distance
    md = np.zeros(ROIs_transformed.shape[0])
    for i in range(ROIs_transformed.shape[0]):
        md[i] = mahalanobis( ROIs_transformed_mean, ROIs_transformed[i], VI) ** 2

    return np.sqrt(md)
    
        
