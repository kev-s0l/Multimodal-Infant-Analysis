import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def plot_acceleration_magnitude(epoch_features, output_plot_name):
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.figure(figsize=(15, 7))

    plt.plot(
        epoch_features.index,
        epoch_features['mean'],
        label='Mean Acceleration',
        color='royalblue'
    )

    plt.fill_between(
        epoch_features.index,
        epoch_features['mean'] - epoch_features['std'],
        epoch_features['mean'] + epoch_features['std'],
        color='lightblue',
        alpha=0.5,
        label='Standard Deviation'
    )

    plt.title('Mean Acceleration Magnitude Over Time', fontsize=16)
    plt.xlabel('Time', fontsize=12)
    plt.ylabel('Acceleration Magnitude', fontsize=12)

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.legend()

    plt.tight_layout()
    plt.savefig(output_plot_name)

    print(f"Successfully generated and saved {output_plot_name}")