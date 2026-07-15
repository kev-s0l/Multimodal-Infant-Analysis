import pandas as pd
import datetime
import re
import h5py
import numpy as np


def parse_sleep_start_info(sleep_file):
    file_date = None
    start_clock_time = None

    with open(sleep_file, 'r', errors='ignore') as f:
        for line in f:
            if "Start Time" in line:
                match = re.search(
                    r'(\d{1,2})/(\d{1,2})/(\d{4})\s+(\d{1,2}):(\d{2}):(\d{2})\s*(AM|PM)',
                    line
                )
                if match:
                    month, day, year, hour, minute, second, meridiem = match.groups()
                    hour = int(hour)

                    if meridiem.upper() == 'PM' and hour != 12:
                        hour += 12
                    if meridiem.upper() == 'AM' and hour == 12:
                        hour = 0

                    file_date = datetime.date(int(year), int(month), int(day))
                    start_clock_time = datetime.time(hour, int(minute), int(second))
                    break

    if file_date is None:
        name_match = re.search(r'(\d{8})', sleep_file)
        if name_match:
            file_date = datetime.datetime.strptime(
                name_match.group(1), '%Y%m%d'
            ).date()

    if file_date is None:
        raise ValueError("Recording date not found.")

    sleep_start_dt = datetime.datetime.combine(
        file_date,
        start_clock_time or datetime.time(0, 0, 0)
    )

    return file_date, start_clock_time, sleep_start_dt


def load_sleep_states(sleep_file, file_date):
    sleep_data = []

    with open(sleep_file, 'r', errors='ignore') as f:
        for line in f:
            if ';' not in line:
                continue

            time_part, state = line.strip().split(';')

            try:
                time_obj = datetime.datetime.strptime(
                    time_part.strip(), '%H:%M:%S,%f'
                ).time()
                full_time = datetime.datetime.combine(file_date, time_obj)
                sleep_data.append((full_time, state.strip()))
            except ValueError:
                continue

    sleep_df = (
        pd.DataFrame(sleep_data, columns=['timestamp', 'state'])
        .set_index('timestamp')
        .sort_index()
    )

    if sleep_df.empty:
        raise ValueError("No sleep data found.")

    sleep_df['state_norm'] = sleep_df['state'].str.lower().str.strip()
    return sleep_df


def load_accelerometer_data(filename, targetID):
    with h5py.File(filename, 'r') as f:
        base = f"Sensors/{targetID}"
        acc_data = np.array(f[f'{base}/Accelerometer'][:], dtype=np.float64)
        time_raw = np.array(f[f'{base}/Time'][:], dtype=np.float64)
        time_dt = np.array([
            datetime.datetime.fromtimestamp(t * 1e-6)
            for t in time_raw
        ])

    return acc_data, time_dt