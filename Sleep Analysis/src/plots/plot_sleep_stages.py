# src/plots/plot_sleep_stages.py
import argparse
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import timedelta
from src.core.sleep_stages_core import compute_sleep_stages_from_edf

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot sleep stages from EDF")
    parser.add_argument("edf_path", help="Path to EDF file")
    parser.add_argument("--out", default="Graphs", help="Output folder for plots")
    args = parser.parse_args()

    df, summary, start_time = compute_sleep_stages_from_edf(args.edf_path)

    os.makedirs(args.out, exist_ok=True)

    # Build time axis
    if start_time is not None:
        times = [start_time + timedelta(seconds=row["start_sec"]) for _, row in df.iterrows()]
    else:
        times = df["start_sec"]

    y = df["stage_code"]

    plt.figure(figsize=(15, 6))
    plt.step(times, y, where="post")
    plt.yticks([1, 2, 3, 4, 5], ["Wake", "Movement", "Transitional", "NREM", "REM"])
    plt.xlabel("Time")
    plt.ylabel("Sleep Stage")
    plt.title("Sleep Stages Over Time")
    plt.grid(True)

    if start_time is not None:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.xticks(rotation=45)

    plt.tight_layout()

    out_png = os.path.join(args.out, "sleep_stages_hypnogram.png")
    plt.savefig(out_png, dpi=200)
    plt.close()

    print(f"Saved plot to: {out_png}")
