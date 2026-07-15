import pandas as pd
import datetime
import re
import h5py
import numpy as np


def parse_sleep_start(sleep_file):
    file_date = None
    start_clock_time = None

    with open(sleep_file, "r", errors="ignore") as f:
        for line in f:
            if "Start Time" in line:
                match = re.search(
                    r"(\d{1,2})/(\d{1,2})/(\d{4})\s+(\d{1,2}):(\d{2}):(\d{2})\s*(AM|PM)",
                    line,
                )
                if match:
                    month, day, year, hour, minute, second, meridiem = match.groups()
                    hour = int(hour)

                    if meridiem.upper() == "PM" and hour != 12:
                        hour += 12
                    if meridiem.upper() == "AM" and hour == 12:
                        hour = 0

                    file_date = datetime.date(int(year), int(month), int(day))
                    start_clock_time = datetime.time(hour, int(minute), int(second))
                    break

    if file_date is None:
        name_match = re.search(r"(\d{8})", str(sleep_file))
        if name_match:
            file_date = datetime.datetime.strptime(
                name_match.group(1), "%Y%m%d"
            ).date()

    if file_date is None:
        raise ValueError(f"Recording date not found for sleep file: {sleep_file}")

    return datetime.datetime.combine(
        file_date,
        start_clock_time or datetime.time(0, 0, 0)
    )


def load_sleep_df(sleep_file):
    sleep_start_dt = parse_sleep_start(sleep_file)
    sleep_data = []

    with open(sleep_file, "r", errors="ignore") as f:
        for line in f:
            if ";" not in line:
                continue

            time_part, state = line.strip().split(";")

            try:
                time_obj = datetime.datetime.strptime(
                    time_part.strip(),
                    "%H:%M:%S,%f"
                ).time()
                full_time = datetime.datetime.combine(
                    sleep_start_dt.date(),
                    time_obj
                )
                sleep_data.append((full_time, state.strip()))
            except ValueError:
                continue

    sleep_df = (
        pd.DataFrame(sleep_data, columns=["timestamp", "state"])
        .set_index("timestamp")
        .sort_index()
    )

    if sleep_df.empty:
        raise ValueError(f"No sleep data found in {sleep_file}")

    sleep_df["state_norm"] = sleep_df["state"].str.lower().str.strip()
    return sleep_df, sleep_start_dt


def _pick_single_or_error(options, label, context):
    if len(options) == 1:
        return options[0]
    raise KeyError(f"{label} not found. Options in {context}: {options}")


def _list_group_keys(group):
    return sorted(list(group.keys()))


def load_acc_df(h5_file, target_id):
    with h5py.File(h5_file, "r") as f:
        if "Sensors" not in f:
            raise KeyError(f"Missing 'Sensors' group in {h5_file}")

        sensors = f["Sensors"]
        base_key = str(target_id)

        if base_key not in sensors:
            sensor_keys = _list_group_keys(sensors)
            if len(sensor_keys) == 1:
                base_key = sensor_keys[0]
                print(
                    f"[warn] target_id '{target_id}' not found; "
                    f"using only sensor id '{base_key}' in {h5_file}"
                )
            else:
                raise KeyError(
                    f"target_id '{target_id}' not found. "
                    f"Available sensor ids in {h5_file}: {sensor_keys}"
                )

        base_group = sensors[base_key]
        acc_path = "Accelerometer"
        time_path = "Time"

        if acc_path not in base_group:
            acc_candidates = [
                k for k in _list_group_keys(base_group)
                if "accelerometer" in k.lower()
            ]
            acc_path = _pick_single_or_error(
                acc_candidates,
                "Accelerometer dataset",
                f"Sensors/{base_key}"
            )

        if time_path not in base_group:
            time_candidates = [
                k for k in _list_group_keys(base_group)
                if k.lower() == "time" or "time" in k.lower()
            ]
            time_path = _pick_single_or_error(
                time_candidates,
                "Time dataset",
                f"Sensors/{base_key}"
            )

        acc_data = np.array(base_group[acc_path][:], dtype=np.float64)
        time_raw = np.array(base_group[time_path][:], dtype=np.float64)
        time_dt = np.array([
            datetime.datetime.fromtimestamp(t * 1e-6)
            for t in time_raw
        ])

    acc_df = pd.DataFrame(
        acc_data,
        columns=["ax", "ay", "az"],
        index=pd.to_datetime(time_dt),
    )

    return acc_df