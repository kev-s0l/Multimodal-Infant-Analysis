import numpy as np
import pandas as pd


def compute_acceleration_magnitude(acc_data, time_dt):
    acc_magnitude = np.linalg.norm(acc_data, axis=1)

    df = pd.DataFrame({
        'timestamp': time_dt,
        'acc_magnitude': acc_magnitude
    }).set_index('timestamp')

    return df


def compute_epoch_features(df):
    epoch_features = df['acc_magnitude'].resample('30s').agg(
        ['mean', 'std', 'min', 'max']
    ).dropna()

    if epoch_features.empty:
        raise ValueError("No data available to calculate epoch statistics.")

    return epoch_features