import os
import numpy as np
import pandas as pd


def calculate_speed_stats_df(acc_data, time_raw, time_dt):
    """
    Estimate scalar speed from accelerometer magnitude and compute
    30-second epoch statistics, preserving original logic.
    """
    time_sec = (time_raw - time_raw[0]) * 1e-6
    delta_t = np.gradient(time_sec)

    acc_mag = np.linalg.norm(acc_data, axis=1)

    speed_est = np.cumsum(acc_mag * delta_t)

    df = pd.DataFrame(
        {
            "timestamp": time_dt,
            "speed_est": speed_est,
        }
    ).set_index("timestamp")

    epoch_features = df["speed_est"].resample("30s").agg(["mean", "std", "min", "max"]).dropna()

    if epoch_features.empty:
        raise ValueError("No data available to calculate epoch statistics.")

    return epoch_features


def ensure_output_dir(output_dir="movement_outputs"):
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def build_output_paths(filename, output_dir="movement_outputs"):
    ensure_output_dir(output_dir)

    base_name = os.path.splitext(os.path.basename(filename))[0]
    output_csv_path = os.path.join(output_dir, f"{base_name}_speed_stats.csv")
    output_plot_path = os.path.join(output_dir, f"{base_name}_speed_plot.png")

    return output_csv_path, output_plot_path


def save_speed_stats_csv(epoch_features, output_csv_path):
    epoch_features.to_csv(output_csv_path)