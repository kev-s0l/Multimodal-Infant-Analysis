import os
import h5py
import numpy as np
import datetime


def load_accelerometer_data(filename, target_ID):
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File '{filename}' not found.")

    with h5py.File(filename, 'r') as f:
        if target_ID not in f['Sensors']:
            raise KeyError(
                f"Sensor ID {target_ID} not found in the file. "
                f"Available IDs: {list(f['Sensors'].keys())}"
            )

        base_path = f'Sensors/{target_ID}'

        if 'Accelerometer' not in f[base_path] or 'Time' not in f[base_path]:
            raise KeyError(
                f"Missing Accelerometer or Time data for Sensor {target_ID}"
            )

        acc_data = np.array(f[f'{base_path}/Accelerometer'][:], dtype=np.float64)
        time_raw = np.array(f[f'{base_path}/Time'][:], dtype=np.float64)
        time_dt = np.array(
            [datetime.datetime.fromtimestamp(t * 1e-6) for t in time_raw]
        )

    return acc_data, time_raw, time_dt