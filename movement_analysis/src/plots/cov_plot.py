import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def plot_cov(cov_df, output_plot_path):
    """
    Plot Coefficient of Variation (CoV) over time and save as PNG.
    Preserves original plotting logic.
    """
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.figure(figsize=(15, 7))

    plt.plot(
        cov_df.index,
        cov_df["cov"],
        label="CoV",
        color="green",
        marker="o",
        markersize=3,
        linestyle="-",
    )

    plt.title("Coefficient of Variation (CoV) Over Time", fontsize=16)
    plt.xlabel("Time", fontsize=12)
    plt.ylabel("Coefficient of Variation (Unitless)", fontsize=12)

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

    plt.legend()
    plt.tight_layout()
    plt.savefig(output_plot_path)
    plt.close()