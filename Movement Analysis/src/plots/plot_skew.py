import argparse
import os
import matplotlib.pyplot as plt
from src.core.skew_core import compute_bowley_skew

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot Bowley-Galton skewness over time")
    parser.add_argument("h5_path", help="Path to H5 file")
    parser.add_argument("target_id", help="Sensor ID (e.g., 16162 or XI-016162)")
    parser.add_argument("--out", default="Graphs", help="Output folder")
    args = parser.parse_args()

    skew_df = compute_bowley_skew(args.h5_path, args.target_id)

    os.makedirs(args.out, exist_ok=True)

    plt.style.use("seaborn-v0_8-whitegrid")
    plt.figure(figsize=(15, 7))

    plt.plot(
        skew_df.index,
        skew_df["bowley_skew"],
        label="Bowley Skewness",
        color="purple",
        marker=".",
        linestyle="-",
    )

    plt.axhline(y=0, color="black", linestyle="--", linewidth=1, label="Symmetric (Skew = 0)")

    plt.title("Bowley-Galton Skewness Over Time (30s Epochs)", fontsize=16)
    plt.xlabel("Time", fontsize=12)
    plt.ylabel("Skewness Coefficient", fontsize=12)
    plt.legend()
    plt.tight_layout()

    base = os.path.splitext(os.path.basename(args.h5_path))[0]
    out_png = os.path.join(args.out, f"{base}_bowley_skew_plot.png")

    plt.savefig(out_png)
    plt.close()

    print(f"Successfully generated and saved {out_png}")
