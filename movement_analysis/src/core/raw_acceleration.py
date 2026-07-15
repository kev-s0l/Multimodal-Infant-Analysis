import os
import numpy as np
import pandas as pd


def downsample_accelerometer_data(acc_data, time_dt, step=500):
    """
    Downsample accelerometer data for clearer plotting.
    Preserves original logic using simple slicing.
    """
    if step <= 0:
        raise ValueError("step must be a positive integer.")

    time_sampled = time_dt[::step]
    acc_sampled = acc_data[::step]

    if len(time_sampled) == 0 or len(acc_sampled) == 0:
        raise ValueError("No data available after downsampling.")

    return time_sampled, acc_sampled


def create_raw_accel_dataframe(time_sampled, acc_sampled):
    """
    Create a dataframe for the downsampled raw accelerometer data.
    """
    if acc_sampled.shape[1] < 3:
        raise ValueError("Accelerometer data must have 3 columns for X, Y, Z.")

    raw_accel_df = pd.DataFrame(
        {
            "timestamp": time_sampled,
            "x": acc_sampled[:, 0],
            "y": acc_sampled[:, 1],
            "z": acc_sampled[:, 2],
        }
    )

    return raw_accel_df


def ensure_output_dir(output_dir="movement_outputs"):
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def build_output_paths(filename, output_dir="movement_outputs"):
    """
    Build output paths for CSV and plot using the input filename stem.
    """
    ensure_output_dir(output_dir)

    base_name = os.path.splitext(os.path.basename(filename))[0]
    output_csv_path = os.path.join(output_dir, f"{base_name}_raw_accel.csv")
    output_plot_path = os.path.join(output_dir, f"{base_name}_raw_accel_plot.png")

    return output_csv_path, output_plot_path


def save_raw_accel_csv(raw_accel_df, output_csv_path):
    raw_accel_df.to_csv(output_csv_path, index=False)