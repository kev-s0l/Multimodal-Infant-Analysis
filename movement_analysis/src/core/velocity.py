import os
import numpy as np
import pandas as pd


def calculate_velocity_stats_df(acc_data, time_dt):
    """
    Estimate component-wise velocity from accelerometer data and compute
    30-second epoch statistics, preserving original logic as closely as possible.
    """
    time_sec = np.array(
        [(dt - time_dt[0]).total_seconds() for dt in time_dt],
        dtype=np.float64
    )
    delta_t = np.gradient(time_sec)

    velocity = np.cumsum(acc_data * delta_t[:, None], axis=0)

    df = pd.DataFrame(
        {
            "timestamp": time_dt,
            "vx": velocity[:, 0],
            "vy": velocity[:, 1],
            "vz": velocity[:, 2],
        }
    ).set_index("timestamp")

    epoch_features = df.resample("30s").agg(["mean", "std", "min", "max"]).dropna()
    epoch_features.columns = ["_".join(col).strip() for col in epoch_features.columns.values]

    if epoch_features.empty:
        raise ValueError("No data available to calculate epoch statistics.")

    return epoch_features


def ensure_output_dir(output_dir="movement_outputs"):
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def build_output_paths(filename, output_dir="movement_outputs"):
    ensure_output_dir(output_dir)

    base_name = os.path.splitext(os.path.basename(filename))[0]
    output_csv_path = os.path.join(output_dir, f"{base_name}_velocity_stats.csv")
    output_plot_path = os.path.join(output_dir, f"{base_name}_velocity_plot.png")

    return output_csv_path, output_plot_path


def save_velocity_stats_csv(epoch_features, output_csv_path):
    epoch_features.to_csv(output_csv_path)