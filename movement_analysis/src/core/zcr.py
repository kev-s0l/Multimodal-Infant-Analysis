import os
import numpy as np
import pandas as pd


def zero_crossings(x):
    """Counts the number of times a signal crosses the zero-axis."""
    return np.count_nonzero(np.diff(np.sign(x)))


def calculate_zcr_df(acc_data, time_dt):
    """
    Compute zero-crossing rate of changes in acceleration magnitude
    in 30-second windows, preserving original logic.
    """
    acc_magnitude = np.linalg.norm(acc_data, axis=1)
    diff_mag = np.diff(acc_magnitude)

    df = pd.DataFrame(
        {
            "timestamp": time_dt[1:],
            "diff_mag": diff_mag,
        }
    ).set_index("timestamp")

    zcr_df = (
        df["diff_mag"]
        .resample("30s")
        .apply(zero_crossings)
        .dropna()
        .to_frame(name="zero_crossing_rate")
    )

    if zcr_df.empty:
        raise ValueError("No data available to calculate Zero-Crossing Rate.")

    return zcr_df


def ensure_output_dir(output_dir="movement_outputs"):
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def build_output_paths(filename, output_dir="movement_outputs"):
    ensure_output_dir(output_dir)

    base_name = os.path.splitext(os.path.basename(filename))[0]
    output_csv_path = os.path.join(output_dir, f"{base_name}_zcr.csv")
    output_plot_path = os.path.join(output_dir, f"{base_name}_zcr_plot.png")

    return output_csv_path, output_plot_path


def save_zcr_csv(zcr_df, output_csv_path):
    zcr_df.to_csv(output_csv_path)