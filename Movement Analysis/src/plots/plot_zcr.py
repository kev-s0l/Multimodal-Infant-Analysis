import argparse
import os
import matplotlib.pyplot as plt
from src.core.zcr_core import compute_zcr_stats

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot ZCR over time")
    parser.add_argument("h5_path", help="Path to H5 file")
    parser.add_argument("target_id", help="Sensor ID (e.g., 16162)")
    parser.add_argument("--out", default="Graphs", help="Output folder")
    args = parser.parse_args()

    zcr_df = compute_zcr_stats(args.h5_path, args.target_id)

    os.makedirs(args.out, exist_ok=True)

    plt.style.use("seaborn-v0_8-whitegrid")
    plt.figure(figsize=(15, 7))

    plt.plot(
        zcr_df.index,
        zcr_df["zero_crossing_rate"],
        label="ZCR",
        color="orangered",
        marker="|",
        markersize=5,
        linestyle="-",
    )

    plt.title("Zero-Crossing Rate (Restlessness) Over Time (30s Epochs)", fontsize=16)
    plt.xlabel("Time", fontsize=12)
    plt.ylabel("Zero-Crossing Count per Epoch", fontsize=12)
    plt.legend()
    plt.tight_layout()

    base = os.path.splitext(os.path.basename(args.h5_path))[0]
    out_png = os.path.join(args.out, f"{base}_zcr_plot.png")

    plt.savefig(out_png)
    plt.close()

    print(f"Successfully generated and saved {out_png}")
