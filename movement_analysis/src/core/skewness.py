import os
import numpy as np
import pandas as pd
from scipy.stats import skew


def compute_skew(x):
    return skew(x) if len(x) >= 3 else np.nan


def calculate_skewness_df(acc_data, time_dt):
    """
    Compute skewness of acceleration magnitude in 30-second windows,
    preserving original logic.
    """
    acc_magnitude = np.linalg.norm(acc_data, axis=1)

    df = pd.DataFrame(
        {
            "timestamp": time_dt,
            "acc_magnitude": acc_magnitude,
        }
    ).set_index("timestamp")

    skewness_df = (
        df["acc_magnitude"]
        .resample("30s")
        .apply(compute_skew)
        .dropna()
        .to_frame(name="skewness")
    )

    if skewness_df.empty:
        raise ValueError("No data available to calculate skewness.")

    return skewness_df


def ensure_output_dir(output_dir="movement_outputs"):
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def build_output_paths(filename, output_dir="movement_outputs"):
    ensure_output_dir(output_dir)

    base_name = os.path.splitext(os.path.basename(filename))[0]
    output_csv_path = os.path.join(output_dir, f"{base_name}_skewness.csv")
    output_plot_path = os.path.join(output_dir, f"{base_name}_skewness_plot.png")

    return output_csv_path, output_plot_path


def save_skewness_csv(skewness_df, output_csv_path):
    skewness_df.to_csv(output_csv_path)