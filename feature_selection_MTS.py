import numpy as np
import pandas as pd



def time_selector(target_features, f, w):
    
    selected_indices = set()
    time_indices = np.random.choice(w, size= target_features // f, replace=False)
    for time in time_indices:
        for s in range(f):
                selected_indices.add(s * w + time)
         
    return sorted(list(selected_indices))[:target_features]    

def sensor_selector(target_features, f, w):
    selected_indices = set()
    sensor_indices = np.random.choice(f, size=target_features // w, replace=False)
    for s in sensor_indices:
        for time in range(w):
            selected_indices.add(s * w + time)
        
    return sorted(list(selected_indices))[:target_features]  


def select_features(data, num_qubits, strategy='b'):
    """
    Select features based on the specified strategy.
    
    Args:
    data (pd.DataFrame): Input data
    num_qubits (int): Number of qubits specified in main
    strategy (str): Feature selection strategy (a, b, c, d, or e)
    
    Returns:
    pd.DataFrame: Data with selected features (including added 0-features if necessary)
    list: Indices of selected features
    """
    num_features = 2**num_qubits - 1 
    original_num_features = data.shape[1]

    # Assume data shape: (samples, features), features = f * w
    f = 5 # set number of sensors
    w = 100# set number of time steps
    

    if strategy == 'a':
        indices = sensor_selector(num_features, f, w)
        selected_data = data.iloc[:, indices]
    elif strategy == 'b':
        indices = time_selector(num_features, f, w)
        selected_data = data.iloc[:, indices]


    return selected_data, indices

