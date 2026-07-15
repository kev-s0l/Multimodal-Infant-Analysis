import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def plot_bowley_skew(skewness_df, output_plot_path):
    """
    Plot Bowley-Galton skewness over time and save as PNG.
    Keeps original plotting logic.
    """
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.figure(figsize=(15, 7))

    plt.plot(
        skewness_df.index,
        skewness_df["bowley_skew"],
        label="Bowley Skewness",
        color="purple",
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

    plt.title("Bowley-Galton Skewness Over Time", fontsize=16)
    plt.xlabel("Time", fontsize=12)
    plt.ylabel("Skewness Coefficient", fontsize=12)

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

    plt.legend()
    plt.tight_layout()
    plt.savefig(output_plot_path)
    plt.close()