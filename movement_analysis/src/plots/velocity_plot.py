import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def plot_velocity_stats(epoch_features, output_plot_path):
    """
    Plot mean estimated velocity components over time and save as PNG.
    Preserves original plotting logic.
    """
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.figure(figsize=(15, 7))

    plt.plot(epoch_features.index, epoch_features["vx_mean"], label="Velocity X (mean)", color="r")
    plt.plot(epoch_features.index, epoch_features["vy_mean"], label="Velocity Y (mean)", color="g")
    plt.plot(epoch_features.index, epoch_features["vz_mean"], label="Velocity Z (mean)", color="b")

    plt.title("Mean Estimated Velocity Components Over Time", fontsize=16)
    plt.xlabel("Time", fontsize=12)
    plt.ylabel("Estimated Velocity (m/s)", fontsize=12)

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

    plt.legend()
    plt.tight_layout()
    plt.savefig(output_plot_path)
    plt.close()