import argparse
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from src.core.raw_stats_core import load_and_sample_raw_accel

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot raw accelerometer data (downsampled)")
    parser.add_argument("h5_path", help="Path to H5 file")
    parser.add_argument("target_id", help="Sensor ID (e.g., 16162 or XI-016162)")
    parser.add_argument("--step", type=int, default=500, help="Downsampling step (default: 500)")
    args = parser.parse_args()

    time_sampled, acc_sampled = load_and_sample_raw_accel(args.h5_path, args.target_id, step=args.step)

    plt.figure(figsize=(12, 6))
    plt.plot(time_sampled, acc_sampled[:, 0], label="X")
    plt.plot(time_sampled, acc_sampled[:, 1], label="Y")
    plt.plot(time_sampled, acc_sampled[:, 2], label="Z")

    plt.title(f"Accelerometer Data - Sensor {args.target_id}")
    plt.xlabel("Time (HH:MM:SS)")
    plt.ylabel("Acceleration (m/s²)")

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    plt.gcf().autofmt_xdate()

    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
