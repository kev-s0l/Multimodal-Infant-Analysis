import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def plot_raw_accelerometer(time_sampled, acc_sampled, target_id, output_plot_path):
    """
    Plot downsampled X, Y, Z accelerometer signals over time and save as PNG.
    Preserves original plotting logic.
    """
    plt.figure(figsize=(12, 6))
    plt.plot(time_sampled, acc_sampled[:, 0], label="X")
    plt.plot(time_sampled, acc_sampled[:, 1], label="Y")
    plt.plot(time_sampled, acc_sampled[:, 2], label="Z")

    plt.title(f"Accelerometer Data - Sensor {target_id}")
    plt.xlabel("Time (HH:MM:SS)")
    plt.ylabel("Acceleration (m/s²)")

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    plt.gcf().autofmt_xdate()

    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_plot_path)
    plt.close()