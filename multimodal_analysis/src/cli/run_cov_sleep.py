import argparse
import os

from core.cov_sleep_loader import (
    parse_sleep_start_info,
    load_sleep_states,
    load_accelerometer_data,
)
from core.cov_sleep_processing import (
    prepare_accelerometer_dataframe,
    compute_cov_30s,
    get_plot_state_config,
)
from core.cov_sleep_analysis import (
    print_start_time_checks,
    run_analytics,
)
from plots.cov_sleep_plot import (
    plot_continuous_cov,
    plot_compressed_sleep_cov,
    plot_cov_distribution_by_state,
    plot_hourly_cov,
)


def main():
    parser = argparse.ArgumentParser(
        description="Continuous + compressed sleep CoV multimodal analysis"
    )

    parser.add_argument("--h5", required=True, help="Path to H5 file")
    parser.add_argument("--sensor-id", required=True, help="Sensor ID")
    parser.add_argument("--sleep-file", required=True, help="Path to sleep profile TXT")
    parser.add_argument("--title-prefix", default="Sleep CoV Analysis", help="Plot title prefix")

    args = parser.parse_args()

    if not os.path.exists(args.h5):
        raise FileNotFoundError(f"H5 file not found: {args.h5}")

    if not os.path.exists(args.sleep_file):
        raise FileNotFoundError(f"Sleep file not found: {args.sleep_file}")

    file_date, start_clock_time, sleep_start_dt = parse_sleep_start_info(args.sleep_file)
    sleep_df = load_sleep_states(args.sleep_file, file_date)

    acc_data, time_dt = load_accelerometer_data(args.h5, args.sensor_id)
    acc_df = prepare_accelerometer_dataframe(acc_data, time_dt)
    cov_30s = compute_cov_30s(acc_df)

    plot1_states, plot1_colors, sleep_states, sleep_colors = get_plot_state_config()

    print_start_time_checks(acc_df, cov_30s, sleep_df)

    plot_continuous_cov(
        cov_30s,
        sleep_df,
        plot1_states,
        plot1_colors,
        f"Continuous Movement Variability (CoV) Across Sleep and Wake - {args.title_prefix}"
    )

    plot_compressed_sleep_cov(
        cov_30s,
        sleep_df,
        sleep_start_dt,
        sleep_states,
        sleep_colors,
        f"REM Sleep Movement CoV Aligned to Pseudo-Timeline - {args.title_prefix}"
    )

    state_cov, hourly_cov = run_analytics(
        cov_30s,
        sleep_df,
        plot1_states,
        sleep_states,
        acc_df
    )

    if not state_cov.empty:
        plot_cov_distribution_by_state(state_cov, plot1_states)

    plot_hourly_cov(hourly_cov)


if __name__ == "__main__":
    main()