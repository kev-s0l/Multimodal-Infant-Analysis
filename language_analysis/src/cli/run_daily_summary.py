import os
import pandas as pd

from core.daily_summary import calculate_daily_totals
from plots.daily_summary_plot_logic import plot_daily_summary


def load_data(data_folder):
    print(f"Loading data from {data_folder}...")

    try:
        recording_info = pd.read_csv(
            os.path.join(data_folder, "recording_info.csv")
        )
        segments = pd.read_csv(
            os.path.join(data_folder, "segments.csv")
        )
        conversations = pd.read_csv(
            os.path.join(data_folder, "conversations.csv")
        )

        print("Loaded recording info, segments, and conversations.")
        return recording_info, segments, conversations

    except FileNotFoundError as e:
        print(
            f"Error: {e}. Please ensure all CSV files are in "
            f"'{data_folder}'."
        )
        return None, None, None


def main():
    data_folder = "lena_extraction_output"

    recording_info, segments, conversations = load_data(data_folder)

    if recording_info is None:
        return

    daily_summary = calculate_daily_totals(
        recording_info,
        segments,
        conversations
    )

    if daily_summary is None or daily_summary.empty:
        print("No daily summary data was created.")
        return

    print(daily_summary.head())

    plot_daily_summary(daily_summary)

    print("\nAnalysis complete!")


if __name__ == "__main__":
    main()