import argparse
import os

from core.h5_loader import load_accelerometer_data
from core.accel_magnitude import (
    compute_acceleration_magnitude,
    compute_epoch_features,
)
from plots.accel_magnitude_plot import plot_acceleration_magnitude


def main():
    parser = argparse.ArgumentParser(
        description="Run acceleration magnitude analysis on H5 sensor data"
    )

    parser.add_argument(
        "--h5",
        required=True,
        help="Path to the H5 file"
    )

    parser.add_argument(
        "--sensor-id",
        required=True,
        help="Sensor ID to analyze"
    )

    args = parser.parse_args()

    filename = args.h5
    target_ID = args.sensor_id

    if not os.path.exists(filename):
        print(f"File '{filename}' not found in the current directory.")
        print("Please upload your H5 file. The script will proceed assuming the file will be available.")
        return

    acc_data, _, time_dt = load_accelerometer_data(filename, target_ID)

    df = compute_acceleration_magnitude(acc_data, time_dt)
    epoch_features = compute_epoch_features(df)

    print("\n--- Acceleration Magnitude Statistics ---")
    print(epoch_features.head())

    output_dir = "movement_outputs"
    os.makedirs(output_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(filename))[0]

    output_csv_name = os.path.join(
        output_dir,
        f"{base_name}_acc_magnitude_per_epoch.csv"
    )
    epoch_features.to_csv(output_csv_name)
    print(f"\nSaved epoch statistics to {output_csv_name}")

    output_plot_name = os.path.join(
        output_dir,
        f"{base_name}_acceleration_magnitude_plot.png"
    )
    plot_acceleration_magnitude(epoch_features, output_plot_name)


if __name__ == "__main__":
    main()