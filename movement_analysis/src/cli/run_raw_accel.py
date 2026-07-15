import argparse

from core.h5_loader import load_accelerometer_data
from core.raw_accel import (
    downsample_accelerometer_data,
    create_raw_accel_dataframe,
    build_output_paths,
    save_raw_accel_csv,
)
from plots.raw_accel_plot import plot_raw_accelerometer


def main():
    parser = argparse.ArgumentParser(
        description="Visualize raw accelerometer data from an H5 file."
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
    parser.add_argument(
        "--step",
        type=int,
        default=500,
        help="Downsampling step size for plotting (default: 500)",
    )

    args = parser.parse_args()

    acc_data, _, time_dt = load_accelerometer_data(args.h5, args.sensor_id)
    time_sampled, acc_sampled = downsample_accelerometer_data(
        acc_data,
        time_dt,
        step=args.step,
    )

    raw_accel_df = create_raw_accel_dataframe(time_sampled, acc_sampled)
    output_csv_path, output_plot_path = build_output_paths(args.h5)

    save_raw_accel_csv(raw_accel_df, output_csv_path)
    print(f"Saved raw accelerometer data to {output_csv_path}")

    plot_raw_accelerometer(
        time_sampled,
        acc_sampled,
        args.sensor_id,
        output_plot_path,
    )
    print(f"Successfully generated and saved {output_plot_path}")


if __name__ == "__main__":
    main()