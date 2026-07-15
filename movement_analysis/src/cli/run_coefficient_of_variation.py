import argparse

from core.h5_loader import load_accelerometer_data
from core.cov import (
    calculate_cov_df,
    build_output_paths,
    save_cov_csv,
)
from plots.cov_plot import plot_cov


def main():
    parser = argparse.ArgumentParser(
        description="Compute Coefficient of Variation (CoV) from accelerometer data in an H5 file."
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
    cov_df = calculate_cov_df(acc_data, time_dt)

    print("\n--- Coefficient of Variation (CoV) ---")
    print(cov_df.head())

    output_csv_path, output_plot_path = build_output_paths(args.h5)

    save_cov_csv(cov_df, output_csv_path)
    print(f"\nSaved CoV data to {output_csv_path}")

    plot_cov(cov_df, output_plot_path)
    print(f"Successfully generated and saved {output_plot_path}")


if __name__ == "__main__":
    main()