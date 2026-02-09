import argparse
import os
import matplotlib.pyplot as plt
from src.core.speed_core import compute_speed_stats

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot scalar speed over time")
    parser.add_argument("h5_path", help="Path to H5 file")
    parser.add_argument("target_id", help="Sensor ID (e.g., 16162 or XI-016162)")
    parser.add_argument("--out", default="Graphs", help="Output folder")
    args = parser.parse_args()

    epoch_features = compute_speed_stats(args.h5_path, args.target_id)

    os.makedirs(args.out, exist_ok=True)

    plt.style.use("seaborn-v0_8-whitegrid")
    plt.figure(figsize=(15, 7))

    plt.plot(epoch_features.index, epoch_features["mean"], label="Mean Estimated Speed", color="darkorange")

    plt.fill_between(
        epoch_features.index,
        epoch_features["min"],
        epoch_features["max"],
        color="moccasin",
        alpha=0.5,
        label="Min-Max Range",
    )

    plt.title("Estimated Scalar Speed Over Time (30s Epochs)", fontsize=16)
    plt.xlabel("Time", fontsize=12)
    plt.ylabel("Estimated Speed (m/s)", fontsize=12)
    plt.legend()
    plt.tight_layout()

    base = os.path.splitext(os.path.basename(args.h5_path))[0]
    out_png = os.path.join(args.out, f"{base}_speed_plot.png")

    plt.savefig(out_png)
    plt.close()

    print(f"Successfully generated and saved {out_png}")
