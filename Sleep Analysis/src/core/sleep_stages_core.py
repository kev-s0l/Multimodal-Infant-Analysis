# src/core/sleep_stages_core.py
import numpy as np
import pandas as pd
import mne
from scipy.ndimage import uniform_filter1d
from src.edf_loader import load_and_preprocess_edf

frequency_bands = {
    "Delta": (0.5, 3.0),
    "Theta": (4, 8),
    "Alpha": (8, 12),
}

def compute_band_power(data, sfreq, band):
    psd, freqs = mne.time_frequency.psd_array_welch(
        data, sfreq=sfreq, fmin=band[0], fmax=band[1], n_per_seg=256, verbose=False
    )
    return np.sum(psd)

def compute_sleep_stages_from_edf(edf_path, epoch_sec=30):
    raw, data, sfreq, start_time, eog_artifacts, ecg_artifacts = load_and_preprocess_edf(edf_path)

    num_segments = int(raw.times[-1] // epoch_sec)
    sleep_stages = np.zeros(num_segments, dtype=int)

    for segment in range(num_segments):
        segment_start = int(segment * epoch_sec * sfreq)
        segment_end = int(min(segment_start + epoch_sec * sfreq, data.shape[1]))

        band_powers = {"Delta": [], "Theta": [], "Alpha": []}

        for ch_data in data:
            ch_segment = ch_data[segment_start:segment_end]
            for band, freq_range in frequency_bands.items():
                power = compute_band_power(ch_segment, sfreq, freq_range)
                band_powers[band].append(power)

        delta_power = np.mean(band_powers["Delta"])
        theta_power = np.mean(band_powers["Theta"])
        alpha_power = np.mean(band_powers["Alpha"])

        eog_segment = eog_artifacts[:, segment_start:segment_end]
        ecg_segment = ecg_artifacts[:, segment_start:segment_end]

        eog_activity = np.mean(np.abs(eog_segment))
        ecg_activity = np.mean(np.abs(ecg_segment))

        # ---- Classification logic (from your scripts) ----
        if alpha_power > 0.2 and delta_power < 0.2:
            stage = 1  # Wake
        elif 0.1 <= alpha_power <= 0.2 and 0.15 <= theta_power <= 0.3:
            stage = 3  # Transitional
        elif delta_power > 0.3 and delta_power > 1.5 * theta_power:
            stage = 4  # NREM
        elif theta_power > 1.5 * delta_power and eog_activity > 0.5:
            stage = 5  # REM
        elif delta_power == 0 and theta_power == 0 and ecg_activity > 0.5:
            stage = 1  # Wake
        else:
            stage = 2  # Movement / N1

        sleep_stages[segment] = stage

    # ---- Smoothing (from your script) ----
    sleep_stages_smoothed = uniform_filter1d(sleep_stages, size=3, mode="nearest")
    sleep_stages_smoothed = np.round(sleep_stages_smoothed).astype(int)

    # ---- Build DataFrame ----
    rows = []
    for i, st in enumerate(sleep_stages_smoothed):
        rows.append({
            "epoch": i,
            "start_sec": i * epoch_sec,
            "stage_code": int(st)
        })

    stages_df = pd.DataFrame(rows)

    stage_labels = {
        1: "Wake",
        2: "Movement",
        3: "Transitional",
        4: "NREM",
        5: "REM",
    }
    stages_df["stage"] = stages_df["stage_code"].map(stage_labels)

    # ---- Summary ----
    total_epochs = len(stages_df)
    summary = {
        "total_epochs": total_epochs,
        "total_hours": raw.times[-1] / 3600.0,
    }

    counts = stages_df["stage"].value_counts()
    for stage, cnt in counts.items():
        minutes = cnt * epoch_sec / 60.0
        summary[f"{stage}_minutes"] = minutes
        summary[f"{stage}_percent"] = 100.0 * cnt / total_epochs

    return stages_df, summary, start_time
