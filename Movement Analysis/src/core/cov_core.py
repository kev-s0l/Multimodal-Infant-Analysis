import h5py
import numpy as np
import pandas as pd
import datetime
import os

def compute_cov_stats(h5_path, target_id):
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

    epoch_stats = df["acc_magnitude"].resample("30s").agg(["mean", "std"]).dropna()

    epoch_stats["cov"] = (epoch_stats["std"] / epoch_stats["mean"]).replace([np.inf, -np.inf], 0)

    cov_df = epoch_stats[["cov"]].dropna()

    if cov_df.empty:
        raise ValueError("No data available to calculate Coefficient of Variation.")

    return cov_df
