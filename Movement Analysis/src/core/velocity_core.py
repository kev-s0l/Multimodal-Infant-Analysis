import h5py
import numpy as np
import pandas as pd
import datetime
import os

def compute_velocity_stats(h5_path, target_id):
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

    time_sec = (time_raw - time_raw[0]) * 1e-6
    delta_t = np.gradient(time_sec)

    velocity = np.cumsum(acc_data * delta_t[:, None], axis=0)

    df = pd.DataFrame({
        "timestamp": time_dt,
        "vx": velocity[:, 0],
        "vy": velocity[:, 1],
        "vz": velocity[:, 2],
    }).set_index("timestamp")

    epoch_features = df.resample("30s").agg(["mean", "std", "min", "max"]).dropna()
    epoch_features.columns = ["_".join(col).strip() for col in epoch_features.columns.values]

    if epoch_features.empty:
        raise ValueError("No data available to calculate epoch statistics.")

    return epoch_features
