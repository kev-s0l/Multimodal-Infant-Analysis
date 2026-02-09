# src/plots/plot_sleep_profile.py
import argparse
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from src.core.sleep_profile_core import parse_sleep_profile, STAGE_VALUES

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot Sleep Profile")
    parser.add_argument("txt_path", help="Path to Sleep profile.txt")
    parser.add_argument("--out", default="Graphs", help="Output folder")
    args = parser.parse_args()

    df, summary = parse_sleep_profile(args.txt_path)

    os.makedirs(args.out, exist_ok=True)

    # Anchor times to today for plotting
    start_datetime = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    times = [
        start_datetime.replace(hour=t.hour, minute=t.minute, second=t.second)
        for t in df["time"]
    ]

    y = df["stage_code"]

    plt.figure(figsize=(15, 6))
    plt.plot(times, y, drawstyle="steps-post", linewidth=2)

    plt.yticks(list(STAGE_VALUES.values()), list(STAGE_VALUES.keys()))
    plt.xlabel("Time")
    plt.ylabel("Sleep Stage")
    plt.title("Sleep Profile Analysis")
    plt.grid(True, alpha=0.3)

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=15))
    plt.xticks(rotation=45)

    plt.tight_layout()

    out_png = os.path.join(args.out, "sleep_profile.png")
    plt.savefig(out_png, dpi=200)
    plt.close()

    print(f"Saved plot to: {out_png}")
