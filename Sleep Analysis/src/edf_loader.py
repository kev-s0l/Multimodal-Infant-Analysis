# src/edf_loader.py
import mne
import numpy as np
import datetime
import pandas as pd
import warnings

warnings.filterwarnings("ignore")

def load_and_preprocess_edf(edf_path):
    raw = mne.io.read_raw_edf(edf_path, preload=True, verbose=False)

    # ---- Start time handling (from your script) ----
    start_time = raw.info.get("meas_date", None)
    if isinstance(start_time, np.datetime64):
        start_time = pd.to_datetime(str(start_time)).to_pydatetime()
    elif isinstance(start_time, (tuple, list)):
        start_time = datetime.datetime.fromtimestamp(start_time[0] + start_time[1] * 1e-6)
    elif not isinstance(start_time, datetime.datetime):
        start_time = None

    # ---- Channel mapping ----
    mapping = {
        "E1:M2": "eog",
        "E2:M2": "eog",
    }
    raw.set_channel_types(mapping)

    selected_channels = [
        "E1:M2", "E2:M2",
        "F4:M1", "F3:M2", "C4:M1", "C3:M2", "O2:M1", "O1:M2",
        "EMG1", "EMG2", "EMG3",
        "ECG II"
    ]
    available_channels = raw.info["ch_names"]
    selected_channels = [ch for ch in selected_channels if ch in available_channels]
    raw.pick_channels(selected_channels)

    # ---- Filter ----
    raw.filter(l_freq=0.5, h_freq=30.0, fir_design="firwin", verbose=False)

    # ---- ICA ----
    ica = mne.preprocessing.ICA(n_components=None, random_state=42, max_iter=300)
    eog_artifacts = np.zeros((len(selected_channels), raw.n_times))
    ecg_artifacts = np.zeros((len(selected_channels), raw.n_times))

    try:
        print(f"Fitting ICA to data using {len(selected_channels)} channels.")
        ica.fit(raw)

        eog_indices, _ = ica.find_bads_eog(raw)
        ecg_indices, _ = ica.find_bads_ecg(raw)

        if eog_indices:
            eog_artifacts = ica.get_sources(raw).get_data(picks=eog_indices)
        if ecg_indices:
            ecg_artifacts = ica.get_sources(raw).get_data(picks=ecg_indices)

        ica.exclude = list(set(eog_indices + ecg_indices))
        ica.apply(raw)
        print("ICA successfully applied.")
    except Exception as e:
        print(f"ICA skipped due to error: {e}")

    data = raw.get_data(return_times=False)
    sfreq = raw.info["sfreq"]

    return raw, data, sfreq, start_time, eog_artifacts, ecg_artifacts
