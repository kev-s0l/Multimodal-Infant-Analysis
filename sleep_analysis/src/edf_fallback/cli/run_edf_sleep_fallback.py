import argparse
import datetime
import pandas as pd

from core.edf_loader import load_edf_file, extract_start_time
from core.yasa_engine import run_yasa_sleep_staging
from core.infant_mapper import (
    map_yasa_hypnogram_to_infant,
    infant_hypnogram_as_int,
)
from plot.fallback_hypnogram_plot import plot_sleep_stages


def main():
    parser = argparse.ArgumentParser(
        description="Run EDF fallback sleep staging using YASA + infant wrapper"
    )

    parser.add_argument(
        "--edf",
        required=True,
        help="Path to the EDF file"
    )

    parser.add_argument(
        "--eeg",
        default="C4:M1",
        help="EEG channel name"
    )

    parser.add_argument(
        "--eog",
        default="E1:M2",
        help="EOG channel name"
    )

    parser.add_argument(
        "--emg",
        default="EMG1",
        help="EMG channel name"
    )

    parser.add_argument(
        "--use-movement",
        action="store_true",
        help="Allow low-confidence WAKE epochs to be relabeled as Movement"
    )

    args = parser.parse_args()

    raw = load_edf_file(args.edf)
    start_time = extract_start_time(raw)

    y_pred, proba, confidence = run_yasa_sleep_staging(
        raw,
        eeg_name=args.eeg,
        eog_name=args.eog,
        emg_name=args.emg,
        metadata=None,
    )

    infant_stages = map_yasa_hypnogram_to_infant(
        y_pred,
        confidence=confidence,
        use_movement=args.use_movement,
    )

    infant_stage_ints = infant_hypnogram_as_int(infant_stages)

    if start_time is not None:
        epoch_times = [
            start_time + datetime.timedelta(seconds=30 * i)
            for i in range(len(infant_stage_ints))
        ]
    else:
        epoch_times = list(range(len(infant_stage_ints)))

    print(infant_stages.value_counts())
    print("Raw YASA predictions preview:")
    print(y_pred[:20])

    print("Unique YASA stage labels:")
    print(set(map(str, y_pred)))

    print("Raw YASA stage counts:")
    print(pd.Series(y_pred).value_counts())
    plot_sleep_stages(epoch_times, infant_stage_ints)


if __name__ == "__main__":
    main()