import argparse
from core.txt_sleep_profile_loader import parse_sleep_profile
from core.txt_sleep_profile_stats import calculate_sleep_statistics
from plots.txt_sleep_profile_plot import plot_sleep_profile


def main():
    parser = argparse.ArgumentParser(
        description="Parse and visualize infant sleep profile text data"
    )

    parser.add_argument(
        "--sleep-file",
        required=True,
        help="Path to the sleep profile text file"
    )

    args = parser.parse_args()
    sleep_file = args.sleep_file

    try:
        timestamps, sleep_stages = parse_sleep_profile(sleep_file)

        print(f"Successfully parsed {len(timestamps)} data points")
        print(f"Sleep stages found: {set(sleep_stages)}")

        _, stage_minutes, stage_percentages = calculate_sleep_statistics(
            sleep_stages
        )

        print("\nSleep Statistics:")
        print("-" * 40)

        for stage in ["Wake", "Movement", "Transitional", "NREM", "REM"]:
            if stage in stage_minutes:
                print(
                    f"{stage:12}: {stage_minutes[stage]:6.1f} min "
                    f"({stage_percentages[stage]:5.1f}%)"
                )

        plot_sleep_profile(timestamps, sleep_stages)

    except FileNotFoundError:
        print(f"Could not find file '{sleep_file}'")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()