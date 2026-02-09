import h5py
import numpy as np
import datetime
import os

def load_and_sample_raw_accel(h5_path, target_id, step=500):
    if not os.path.exists(h5_path):
        raise FileNotFoundError(f"File '{h5_path}' not found.")

    with h5py.File(h5_path, "r") as f:
        if target_id not in f["Sensors"]:
            raise KeyError(f"Sensor ID {target_id} not found. Available IDs: {list(f['Sensors'].keys())}")

        base_path = f"Sensors/{target_id}"
        if "Accelerometer" not in f[base_path] or "Time" not in f[base_path]:
            raise KeyError(f"Missing Accelerometer or Time data for Sensor {target_id}")

        acc_data = f[f"{base_path}/Accelerometer"][:]
        time_raw = f[f"{base_path}/Time"][:]

    time_dt = [datetime.datetime.fromtimestamp(t * 1e-6) for t in time_raw]

    time_sampled = time_dt[::step]
    acc_sampled = acc_data[::step]

    return time_sampled, acc_sampled
