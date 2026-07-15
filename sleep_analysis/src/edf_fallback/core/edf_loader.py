import mne
import numpy as np
import datetime
import pandas as pd

def load_edf_file(edf_file_path):
    raw = mne.io.read_raw_edf(edf_file_path, preload=True)
    return raw

def extract_start_time(raw):
    start_time = raw.info["meas_date"]

    if isinstance(start_time, np.datetime64):
        start_time = pd.to_datetime(str(start_time)).to_pydatetime()
    elif isinstance(start_time, (tuple, list)):
        start_time = datetime.datetime.fromtimestamp(start_time[0] +start_time[1] * 1e-6)
    elif not isinstance(start_time, datetime.datetime):
        start_time = None

    return start_time

def prepare_eeg_channels(raw):
    mapping = {
        "E1:M2": "eog",
        "E2:M2": "eog",
    }
    raw.set_channel_types(mapping)

    selected_channels = [
        "F4:M1", "F3:M2", "C4:M1", "C3:M2", "O2:M1", "O1:M2",
    ]

    available_channels = raw.info["ch_names"]
    selected_channels = [
        ch for ch in selected_channels if ch in available_channels
    ]

    raw.pick_channels(selected_channels)
    raw.filter(0.5, 30, fir_design="firwin")

    return raw, selected_channels