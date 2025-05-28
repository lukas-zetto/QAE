import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import os
import pickle

def create_sliding_windows_from_csv(
    csv_path, 
    window_size=10, 
    stride=1, 
    save_output=False, 
    output_dir='sliding_windows_data'
):
    """
    Liest die CSV ein, erstellt Sliding Windows und normalisiert analog zu goldstein_uchida_preprocess.

    Args:
        csv_path (str): Pfad zur CSV-Datei.
        window_size (int): Größe des Sliding Windows.
        stride (int): Schrittweite.
        save_output (bool): Speichert die Sliding Windows und Metadaten.
        output_dir (str): Zielverzeichnis.

    Returns:
        np.ndarray: Sliding Windows (Samples x Features).
        dict: Mapping von Original- zu Window-Indizes.
    """
    # CSV einlesen und pivotieren
    df = pd.read_csv(csv_path, sep=';', decimal='.', encoding='utf-8')
    df_pivot = df.pivot(index='datetime', columns='id', values='value')
    df_pivot = df_pivot.sort_index()

    # Normalisierung wie in goldstein_uchida_preprocess
    scaler = StandardScaler()
    data = pd.DataFrame(scaler.fit_transform(df_pivot), columns=df_pivot.columns)
    data = range_based_normalize(data)

    T, f = data.shape
    windows = []
    window_indices = []

    for start in range(0, T - window_size + 1, stride):
        window = data.iloc[start:start + window_size].values
        window_flat = window.T.flatten()
        windows.append(window_flat)
        window_indices.append(start)  # Mapping: Startindex → Window

    X_windows = np.array(windows)
    original_to_window = dict(zip(window_indices, range(len(window_indices))))

    if save_output:
        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(csv_path))[0]
        np.save(os.path.join(output_dir, f'{base_name}_windows.npy'), X_windows)
        with open(os.path.join(output_dir, f'{base_name}_original_to_window.pkl'), 'wb') as f:
            pickle.dump(original_to_window, f)
        print(f"Sliding windows und Mapping gespeichert in {output_dir}")

    return X_windows, original_to_window, window_size

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
        normalized_data[column] = ((data[column] - min_val) / (max_val - min_val)) * max_value

    return normalized_data