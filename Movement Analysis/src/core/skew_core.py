import h5py
import numpy as np
import pandas as pd
import datetime
import os

def bowley_skew(x):
    if len(x) < 4:
        return np.nan
    q1 = np.percentile(x, 25)
    q2 = np.percentile(x, 50)
    q3 = np.percentile(x, 75)
    denominator = q3 - q1
    if denominator == 0:
        return 0
    return (q3 + q1 - 2 * q2) / denominator

def compute_bowley_skew(h5_path, target_id):
    if not os.path.exists(h5_path):
        raise FileNotFoundError(f"File '{h5_path}' not found.")

    with h5py.File(h5_path, "r") as f:
        if target_id not in f["Sensors"]:
            raise KeyError(f"Sensor ID {target_id} not found. Available IDs: {list(f['Sensors'].keys())}")

        base_path = f"Sensors/{target_id}"
        if "Accelerometer" not in f[base_path] or "Time" not in f[base_path]:
            raise KeyError(f"Missing Accelerometer or Time data for Sensor {target_id}")

        acc_data = np.array(f[f"{base_path}/Accelerometer"][:], dtype=np.float64)
        time_raw = np.array(f[f"{base_path}/Time"][:], dtype=np.float64)
        time_dt = np.array([datetime.datetime.fromtimestamp(t * 1e-6) for t in time_raw])

    acc_magnitude = np.linalg.norm(acc_data, axis=1)
    df = pd.DataFrame({"timestamp": time_dt, "acc_magnitude": acc_magnitude}).set_index("timestamp")

    skewness_df = (
        df["acc_magnitude"]
        .resample("30s")
        .apply(bowley_skew)
        .dropna()
        .to_frame(name="bowley_skew")
    )

    if skewness_df.empty:
        raise ValueError("No data available to calculate skewness.")

    return skewness_df
