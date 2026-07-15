import argparse

from core.h5_loader import load_accelerometer_data
from core.speed import (
    calculate_speed_stats_df,
    build_output_paths,
    save_speed_stats_csv,
)
from plots.speed_plot import plot_speed_stats


def main():
    parser = argparse.ArgumentParser(
        description="Compute estimated scalar speed statistics from accelerometer data in an H5 file."
    )
    parser.add_argument(
        "--h5",
        required=True,
        help="Path to the input H5 file",
    )
    parser.add_argument(
        "--sensor-id",
        required=True,
        help="Target sensor ID inside the H5 file",
    )

    args = parser.parse_args()

    acc_data, time_raw, time_dt = load_accelerometer_data(args.h5, args.sensor_id)
    epoch_features = calculate_speed_stats_df(acc_data, time_raw, time_dt)

    print("\n--- Estimated Scalar Speed Stats ---")
    print(epoch_features.head())

    output_csv_path, output_plot_path = build_output_paths(args.h5)

    save_speed_stats_csv(epoch_features, output_csv_path)
    print(f"\nSaved speed statistics to {output_csv_path}")

    plot_speed_stats(epoch_features, output_plot_path)
    print(f"Successfully generated and saved {output_plot_path}")


if __name__ == "__main__":
    main()