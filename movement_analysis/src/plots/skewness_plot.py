import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def plot_skewness(skewness_df, output_plot_path):
    """
    Plot skewness of acceleration magnitude over time and save as PNG.
    Preserves original plotting logic.
    """
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.figure(figsize=(15, 7))

    plt.plot(
        skewness_df.index,
        skewness_df["skewness"],
        label="Skewness",
        color="teal",
        marker=".",
        linestyle="-",
    )

    plt.axhline(
        y=0,
        color="black",
        linestyle="--",
        linewidth=1,
        label="Symmetric (Skew = 0)",
    )

    plt.title("Skewness of Acceleration Magnitude Over Time", fontsize=16)
    plt.xlabel("Time", fontsize=12)
    plt.ylabel("Skewness Coefficient", fontsize=12)

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    plt.xticks(rotation=45)

    plt.legend()
    plt.tight_layout()
    plt.savefig(output_plot_path)
    plt.close()