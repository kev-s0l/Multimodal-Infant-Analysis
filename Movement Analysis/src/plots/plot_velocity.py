import argparse
import os
import matplotlib.pyplot as plt
from src.core.velocity_core import compute_velocity_stats

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot component-wise velocity stats")
    parser.add_argument("h5_path", help="Path to H5 file")
    parser.add_argument("target_id", help="Sensor ID (e.g., 16162)")
    parser.add_argument("--out", default="Graphs", help="Output folder")
    args = parser.parse_args()

    df = compute_velocity_stats(args.h5_path, args.target_id)

    os.makedirs(args.out, exist_ok=True)

    plt.style.use("seaborn-v0_8-whitegrid")
    plt.figure(figsize=(15, 7))

    plt.plot(df.index, df["vx_mean"], label="Velocity X (mean)", color="r")
    plt.plot(df.index, df["vy_mean"], label="Velocity Y (mean)", color="g")
    plt.plot(df.index, df["vz_mean"], label="Velocity Z (mean)", color="b")

    plt.title("Mean Estimated Velocity Components Over Time (30s Epochs)", fontsize=16)
    plt.xlabel("Time", fontsize=12)
    plt.ylabel("Estimated Velocity (m/s)", fontsize=12)
    plt.legend()
    plt.tight_layout()

    base = os.path.splitext(os.path.basename(args.h5_path))[0]
    out_png = os.path.join(args.out, f"{base}_velocity_plot.png")

    plt.savefig(out_png)
    plt.close()

    print(f"Successfully generated and saved {out_png}")
