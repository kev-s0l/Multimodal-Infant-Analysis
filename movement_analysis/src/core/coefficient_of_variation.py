import os
import numpy as np
import pandas as pd


def calculate_cov_df(acc_data, time_dt):
    """
    Compute acceleration magnitude and Coefficient of Variation (CoV)
    in 30-second windows, preserving original logic.
    """
    acc_magnitude = np.linalg.norm(acc_data, axis=1)

    df = pd.DataFrame(
        {
            "timestamp": time_dt,
            "acc_magnitude": acc_magnitude,
        }
    ).set_index("timestamp")

    epoch_stats = df["acc_magnitude"].resample("30s").agg(["mean", "std"]).dropna()

    epoch_stats["cov"] = (epoch_stats["std"] / epoch_stats["mean"]).replace(
        [np.inf, -np.inf], 0
    )

    cov_df = epoch_stats[["cov"]].dropna()

    if cov_df.empty:
        raise ValueError("No data available to calculate Coefficient of Variation.")

    return cov_df


def ensure_output_dir(output_dir="movement_outputs"):
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def build_output_paths(filename, output_dir="movement_outputs"):
    ensure_output_dir(output_dir)

    base_name = os.path.splitext(os.path.basename(filename))[0]
    output_csv_path = os.path.join(output_dir, f"{base_name}_cov.csv")
    output_plot_path = os.path.join(output_dir, f"{base_name}_cov_plot.png")

    return output_csv_path, output_plot_path


def save_cov_csv(cov_df, output_csv_path):
    cov_df.to_csv(output_csv_path)