import os
import numpy as np
import pandas as pd


def bowley_skew(x):
    """Calculates the Bowley-Galton skewness coefficient."""
    if len(x) < 4:
        return np.nan

    q1 = np.percentile(x, 25)
    q2 = np.percentile(x, 50)
    q3 = np.percentile(x, 75)

    denominator = q3 - q1
    if denominator == 0:
        return 0

    return (q3 + q1 - 2 * q2) / denominator


def calculate_bowley_skew_df(acc_data, time_dt):
    """
    Compute acceleration magnitude and Bowley skewness in 30-second windows.
    Keeps original logic/results.
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
        .apply(bowley_skew)
        .dropna()
        .to_frame(name="bowley_skew")
    )

    if skewness_df.empty:
        raise ValueError("No data available to calculate skewness.")

    return skewness_df


def ensure_output_dir(output_dir="movement_outputs"):
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def build_output_paths(filename, output_dir="movement_outputs"):
    """
    Save outputs inside movement_outputs using input filename stem.
    """
    ensure_output_dir(output_dir)

    base_name = os.path.splitext(os.path.basename(filename))[0]
    output_csv_path = os.path.join(output_dir, f"{base_name}_bowley_skew.csv")
    output_plot_path = os.path.join(output_dir, f"{base_name}_bowley_skew_plot.png")

    return output_csv_path, output_plot_path


def save_skewness_csv(skewness_df, output_csv_path):
    skewness_df.to_csv(output_csv_path)