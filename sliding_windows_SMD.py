import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import os
import pickle

def range_based_normalize(data):
    """
    Normalize the data using range-based normalization.
    """
    num_features = data.shape[1]
    max_value = 1 / num_features
    normalized_data = pd.DataFrame()

    for column in data.columns:
        min_val = data[column].min()
        max_val = data[column].max()
        if max_val != min_val:
            normalized_data[column] = ((data[column] - min_val) / (max_val - min_val)) * max_value
        else:
            normalized_data[column] = 0.0  # avoid division by zero

    return normalized_data

def create_sliding_windows_from_csv(
    csv_path,
    window_size=100,
    stride=50,
    save_output=False,
    output_dir='sliding_windows_data'
):
    # 1) Load CSV directly (no datetime/id)
    df = pd.read_csv(csv_path)
    
    # 2) Standardize then range normalize
    scaler = StandardScaler()
    scaled = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)
    data = range_based_normalize(scaled)

    # 3) Create sliding windows
    T, f = data.shape
    windows = []
    window_idx = []

    for start in range(0, T - window_size + 1, stride):
        win = data.iloc[start:start + window_size].values.T.flatten()
        windows.append(win)
        window_idx.append(start)

    # 4) Create column names for flattened windows
    X_windows = pd.DataFrame(windows,
                             columns=[f"{feat}_t{t}"
                                      for feat in data.columns
                                      for t in range(window_size)])
    mapping = dict(zip(window_idx, range(len(window_idx))))

    # 5) Save if needed
    if save_output:
        os.makedirs(output_dir, exist_ok=True)
        base = os.path.splitext(os.path.basename(csv_path))[0]
        X_windows.to_numpy().tofile(f"{output_dir}/{base}_windows.npy")
        with open(f"{output_dir}/{base}_mapping.pkl", "wb") as f:
            pickle.dump(mapping, f)
            
    print(X_windows.shape)

    return X_windows, mapping, window_size
