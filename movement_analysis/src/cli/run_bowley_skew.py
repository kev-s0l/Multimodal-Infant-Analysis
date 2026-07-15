import argparse

from core.h5_loader import load_accelerometer_data
from core.bowley_skew import (
    calculate_bowley_skew_df,
    build_output_paths,
    save_skewness_csv,
)
from plots.bowley_skew_plot import plot_bowley_skew


def main():
    parser = argparse.ArgumentParser(
        description="Compute Bowley-Galton skewness from accelerometer data in an H5 file."
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
    skewness_df = calculate_bowley_skew_df(acc_data, time_dt)

    print("\n--- Bowley-Galton Skewness of Acceleration Magnitude ---")
    print(skewness_df.head())

    output_csv_path, output_plot_path = build_output_paths(args.h5)

    save_skewness_csv(skewness_df, output_csv_path)
    print(f"\nSaved skewness data to {output_csv_path}")

    plot_bowley_skew(skewness_df, output_plot_path)
    print(f"Successfully generated and saved {output_plot_path}")


if __name__ == "__main__":
    main()