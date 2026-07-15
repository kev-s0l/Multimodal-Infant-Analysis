import numpy as np

# Compatibility fix for NumPy >= 2.4
if not hasattr(np, "trapz"):
    np.trapz = np.trapezoid

import yasa


def run_yasa_sleep_staging(
    raw,
    eeg_name="C4:M1",
    eog_name="E1:M2",
    emg_name="EMG1",
    metadata=None,
):
    """
    Run YASA automatic sleep staging on an MNE Raw object.
    """

    available_channels = raw.ch_names

    if eeg_name not in available_channels:
        raise ValueError(
            f"EEG channel '{eeg_name}' not found. "
            f"Available channels: {available_channels}"
        )

    if eog_name is not None and eog_name not in available_channels:
        raise ValueError(
            f"EOG channel '{eog_name}' not found. "
            f"Available channels: {available_channels}"
        )

    if emg_name is not None and emg_name not in available_channels:
        raise ValueError(
            f"EMG channel '{emg_name}' not found. "
            f"Available channels: {available_channels}"
        )

    sls = yasa.SleepStaging(
        raw,
        eeg_name=eeg_name,
        eog_name=eog_name,
        emg_name=emg_name,
        metadata=metadata,
    )

    y_pred = sls.predict()
    proba = sls.predict_proba()
    confidence = proba.max(axis=1)

    return y_pred, proba, confidence