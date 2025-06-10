import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import os
import pickle
from sklearn.decomposition import PCA


# def create_sliding_windows_from_csv(
#     csv_path, 
#     window_size=50, 
#     stride=5, 
#     save_output=False, 
#     output_dir='sliding_windows_data'
# ):
#     """
#     Liest die CSV ein, erstellt Sliding Windows und normalisiert analog zu goldstein_uchida_preprocess.

#     Args:
#         csv_path (str): Pfad zur CSV-Datei.
#         window_size (int): Größe des Sliding Windows.
#         stride (int): Schrittweite.
#         save_output (bool): Speichert die Sliding Windows und Metadaten.
#         output_dir (str): Zielverzeichnis.

#     Returns:
#         np.ndarray: Sliding Windows (Samples x Features).
#         dict: Mapping von Original- zu Window-Indizes.
#     """
#     # CSV einlesen und pivotieren
#     df = pd.read_csv(csv_path, sep=';', decimal='.', encoding='utf-8')
#     df_pivot = df.pivot(index='datetime', columns='id', values='value')
#     df_pivot = df_pivot.sort_index()

#     # Normalisierung wie in goldstein_uchida_preprocess
#     scaler = StandardScaler()
#     data = pd.DataFrame(scaler.fit_transform(df_pivot), columns=df_pivot.columns)
#     data = range_based_normalize(data)

#     scaler = StandardScaler()
#     data = pd.DataFrame(scaler.fit_transform(df_pivot), columns=df_pivot.columns)
#     data = range_based_normalize(data)  # Assuming you have this function

#     # 3. Perform PCA on normalized data (keep all components)
#     pca = PCA()
#     pca.fit(data)

# # 4. Calculate feature importance by summing absolute values of top 3 components' loadings
#     n_top_components = 5
#     components = pca.components_[:n_top_components]  # shape (3, n_features)
#     importance = np.sum(np.abs(components), axis=0)  # shape (n_features,)

# # 5. Select indices of top 3 important features
#     top3_indices = importance.argsort()[::-1][:5]

# # 6. Get the column names of those features
#     top3_features = data.columns[top3_indices]

# # 7. Select only those columns from data
#     data = data[top3_features]

#     T, f = data.shape
#     windows = []
#     window_indices = []

#     for start in range(0, T - window_size + 1, stride):
#         window = data.iloc[start:start + window_size].values
#         window_flat = window.T.flatten()
#         windows.append(window_flat)
#         window_indices.append(start)  # Mapping: Startindex → Window

#     #X_windows = np.array(windows)
#     columns = [f'sensor{s}_t{t}' for s in range(f) for t in range(window_size)]
#     X_windows = pd.DataFrame(windows, columns=columns)

#     original_to_window = dict(zip(window_indices, range(len(window_indices))))

#     if save_output:
#         os.makedirs(output_dir, exist_ok=True)
#         base_name = os.path.splitext(os.path.basename(csv_path))[0]
#         np.save(os.path.join(output_dir, f'{base_name}_windows.npy'), X_windows)
#         with open(os.path.join(output_dir, f'{base_name}_original_to_window.pkl'), 'wb') as f:
#             pickle.dump(original_to_window, f)
#         print(f"Sliding windows und Mapping gespeichert in {output_dir}")

#     return X_windows, original_to_window, window_size

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


def create_sliding_windows_from_csv(
    csv_path,
    window_size=20,
    stride=2,
    save_output=False,
    output_dir='sliding_windows_data'
):
    # 1) Load and pivot
    df = pd.read_csv(csv_path, sep=';', decimal='.')
    df_pivot = df.pivot(index='datetime', columns='id', values='value').sort_index()

    # 2) Standardize then range‑normalize
    scaler = StandardScaler()
    scaled = pd.DataFrame(scaler.fit_transform(df_pivot),
                          index=df_pivot.index,
                          columns=df_pivot.columns)
    data = range_based_normalize(scaled)

    # 3) PCA to pick top-k features
    pca = PCA()
    pca.fit(data)
    comps = pca.components_[:5]
    importance = np.sum(np.abs(comps), axis=0)
    top_feats = data.columns[np.argsort(importance)[-5:]]
    data = data[top_feats]

    # 4) Build windows
    T, f = data.shape
    windows = []
    window_idx = []
    for start in range(0, T - window_size + 1, stride):
        win = data.iloc[start:start + window_size].values.T.flatten()
        windows.append(win)
        window_idx.append(start)

    X_windows = pd.DataFrame(windows,
                             columns=[f"{feat}_t{t}"
                                      for feat in top_feats
                                      for t in range(window_size)])
    mapping = dict(zip(window_idx, range(len(window_idx))))

    if save_output:
        os.makedirs(output_dir, exist_ok=True)
        base = os.path.splitext(os.path.basename(csv_path))[0]
        X_windows.to_numpy().tofile(f"{output_dir}/{base}_windows.npy")
        with open(f"{output_dir}/{base}_mapping.pkl", "wb") as f:
            pickle.dump(mapping, f)

    return X_windows, mapping, window_size
