import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D


def plot_sleep_stages(epoch_times, infant_stage_ints):
    fig, ax = plt.subplots(figsize=(15, 6))
    
    ax.axhspan(0.5, 1.5, color="#f4a261", alpha=0.15)  # Wake
    ax.axhspan(1.5, 2.5, color="#e76f51", alpha=0.15)  # Movement
    ax.axhspan(2.5, 3.5, color="#e9c46a", alpha=0.15)  # Transitional
    ax.axhspan(3.5, 4.5, color="#2a9d8f", alpha=0.15)  # NREM

    # Original step plot
    ax.step(epoch_times, infant_stage_ints, where="post", color="blue")
    # ax.margins(x=0)
    ax.set_xlim(epoch_times[0], epoch_times[-1])

    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(["Wake", "Movement", "Transitional", "NREM", "REM"])

    ax.set_xlabel("Time")
    ax.set_ylabel("Sleep Stage")
    ax.set_title("EDF-Based Sleep Profile Analysis", fontweight="bold")

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_minor_locator(mdates.SecondLocator(bysecond=[0, 30]))

    # Grid styling
    ax.grid(True, which="major", axis="x", alpha=0.35)
    ax.grid(True, which="minor", axis="x", alpha=0.12)

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()