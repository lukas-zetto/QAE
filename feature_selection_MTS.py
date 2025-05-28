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


def select_features(data, num_qubits, strategy='a'):
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
    
    #if the number of features is greater than the original number of features, add zero features rather than selecting features
    if num_features >= original_num_features:
        selected_data = data.copy()
        num_zero_features = num_features - original_num_features
        for i in range(num_zero_features):
            selected_data[f'zero_feature_{i}'] = 0
        return selected_data, list(range(num_features))

    # Assume data shape: (samples, features), features = f * w
    f = ... # set number of sensors
    w = ... # set number of time steps

    if strategy == 'a':
        indices = sensor_selector(num_features, f, w)
        selected_data = data.iloc[:, indices]
        return selected_data  # Only return the selected entries

    elif strategy == 'b':
        indices = time_selector(num_features, f, w)
        selected_data = data.iloc[:, indices]
        return selected_data  # Only return the selected entries

 