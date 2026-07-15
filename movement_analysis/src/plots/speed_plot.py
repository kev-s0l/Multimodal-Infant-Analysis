import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def plot_speed_stats(epoch_features, output_plot_path):
    """
    Plot estimated scalar speed over time and save as PNG.
    Preserves original plotting logic.
    """
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.figure(figsize=(15, 7))

    plt.plot(
        epoch_features.index,
        epoch_features["mean"],
        label="Mean Estimated Speed",
        color="darkorange",
    )

    plt.fill_between(
        epoch_features.index,
        epoch_features["min"],
        epoch_features["max"],
        color="moccasin",
        alpha=0.5,
        label="Min-Max Range",
    )

    plt.title("Estimated Scalar Speed Over Time", fontsize=16)
    plt.xlabel("Time", fontsize=12)
    plt.ylabel("Estimated Speed (m/s)", fontsize=12)

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    plt.xticks(rotation=45)

    plt.legend()
    plt.tight_layout()
    plt.savefig(output_plot_path)
    plt.close()