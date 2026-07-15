import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime


def plot_sleep_profile(timestamps, sleep_stages, output_dir="sleep_visualizations", output_name="sleep_profile_line_graph.png"):
    """
    Plot infant sleep stage progression over time,
    with a different color for each sleep stage.
    """

    stage_values = {
        "Wake": 4,
        "Movement": 3,
        "Transitional": 2,
        "NREM": 1,
        "REM": 0,
    }

    stage_colors = {
        "Wake": "gold",
        "Movement": "orange",
        "Transitional": "purple",
        "NREM": "royalblue",
        "REM": "crimson",
    }

    start_datetime = datetime.today().replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    timestamp_datetimes = [
        start_datetime.replace(
            hour=t.hour,
            minute=t.minute,
            second=t.second
        )
        for t in timestamps
    ]

    y_values = [stage_values.get(stage, -1) for stage in sleep_stages]

    os.makedirs(output_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(15, 6))

    for i in range(len(timestamp_datetimes) - 1):
        stage = sleep_stages[i]
        color = stage_colors.get(stage, "gray")

        ax.plot(
            [timestamp_datetimes[i], timestamp_datetimes[i + 1]],
            [y_values[i], y_values[i]],
            color=color,
            linewidth=2
        )

        # vertical jump to next stage
        ax.plot(
            [timestamp_datetimes[i + 1], timestamp_datetimes[i + 1]],
            [y_values[i], y_values[i + 1]],
            color=color,
            linewidth=2
        )

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=15))
    fig.autofmt_xdate()

    ax.set_yticks(list(stage_values.values()))
    ax.set_yticklabels(list(stage_values.keys()))

    ax.set_xlabel("Time", fontsize=12)
    ax.set_ylabel("Sleep Stage", fontsize=12)
    ax.set_title(
        "Sleep Profile Analysis",
        fontsize=14,
        fontweight="bold"
    )
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    output_path = os.path.join(output_dir, output_name)
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved plot to {output_path}")

    plt.show()