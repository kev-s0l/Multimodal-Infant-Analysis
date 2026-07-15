import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def plot_zcr(zcr_df, output_plot_path):
    """
    Plot zero-crossing rate over time and save as PNG.
    Preserves original plotting logic.
    """
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

    plt.title("Zero-Crossing Rate (Restlessness) Over Time", fontsize=16)
    plt.xlabel("Time", fontsize=12)
    plt.ylabel("Zero-Crossing Count per Epoch", fontsize=12)

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    plt.xticks(rotation=45)

    plt.legend()
    plt.tight_layout()
    plt.savefig(output_plot_path)
    plt.close()