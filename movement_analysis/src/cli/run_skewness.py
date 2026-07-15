import argparse

from core.h5_loader import load_accelerometer_data
from core.skewness import (
    calculate_skewness_df,
    build_output_paths,
    save_skewness_csv,
)
from plots.skewness_plot import plot_skewness


def main():
    parser = argparse.ArgumentParser(
        description="Compute skewness of acceleration magnitude from accelerometer data in an H5 file."
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

    acc_data, _, time_dt = load_accelerometer_data(args.h5, args.sensor_id)
    skewness_df = calculate_skewness_df(acc_data, time_dt)

    print("\n--- Skewness of Acceleration Magnitude ---")
    print(skewness_df.head())

    output_csv_path, output_plot_path = build_output_paths(args.h5)

    save_skewness_csv(skewness_df, output_csv_path)
    print(f"\nSaved skewness data to {output_csv_path}")

    plot_skewness(skewness_df, output_plot_path)
    print(f"Successfully generated and saved {output_plot_path}")


if __name__ == "__main__":
    main()