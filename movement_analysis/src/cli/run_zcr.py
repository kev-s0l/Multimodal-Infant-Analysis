import argparse

from core.h5_loader import load_accelerometer_data
from core.zcr import (
    calculate_zcr_df,
    build_output_paths,
    save_zcr_csv,
)
from plots.zcr_plot import plot_zcr


def main():
    parser = argparse.ArgumentParser(
        description="Compute zero-crossing rate from accelerometer data in an H5 file."
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
    zcr_df = calculate_zcr_df(acc_data, time_dt)

    print("\n--- Zero-Crossing Rate of Motion Change ---")
    print(zcr_df.head())

    output_csv_path, output_plot_path = build_output_paths(args.h5)

    save_zcr_csv(zcr_df, output_csv_path)
    print(f"\nSaved ZCR data to {output_csv_path}")

    plot_zcr(zcr_df, output_plot_path)
    print(f"Successfully generated and saved {output_plot_path}")


if __name__ == "__main__":
    main()