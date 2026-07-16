from __future__ import annotations

import contextlib
import datetime
import io

import pandas as pd

from app.path_utils import load_module, require_path


sleep_loader = load_module(
    "app_sleep_profile_loader",
    "sleep_analysis/src/txt_sleep_profile/core/txt_sleep_profile_loader.py",
)
sleep_stats = load_module(
    "app_sleep_profile_stats",
    "sleep_analysis/src/txt_sleep_profile/core/txt_sleep_profile_stats.py",
)
edf_loader = load_module("app_sleep_edf_loader", "sleep_analysis/src/edf_fallback/core/edf_loader.py")
yasa_engine = load_module("app_sleep_yasa_engine", "sleep_analysis/src/edf_fallback/core/yasa_engine.py")
infant_mapper = load_module("app_sleep_infant_mapper", "sleep_analysis/src/edf_fallback/core/infant_mapper.py")


def run_sleep_analysis(params: dict) -> dict:
    mode = params["mode"]
    if mode == "Text Sleep Profile":
        return _run_text_sleep_profile(params)
    if mode == "EDF Fallback":
        return _run_edf_fallback(params)
    raise ValueError(f"Unsupported sleep mode: {mode}")


def _run_text_sleep_profile(params: dict) -> dict:
    sleep_path = require_path(params["sleep_path"], "Sleep profile")
    timestamps, stages = sleep_loader.parse_sleep_profile(str(sleep_path))
    counts, minutes, percentages = sleep_stats.calculate_sleep_statistics(stages)

    stats_df = pd.DataFrame(
        [
            {
                "stage": stage,
                "epochs": counts[stage],
                "minutes": minutes[stage],
                "percentage": percentages[stage],
            }
            for stage in counts
        ]
    )

    series_df = pd.DataFrame({"timestamp": timestamps, "stage": stages})
    return {
        "message": f"Parsed {len(timestamps)} sleep epochs. No files were written.",
        "tables": [
            {"title": "Sleep Statistics", "data": stats_df},
            {"title": "Sleep Stages", "data": series_df},
        ],
        "figures": [
            {
                "title": "Sleep Profile",
                "kind": "sleep_text_profile",
                "timestamps": timestamps,
                "stages": stages,
            }
        ],
    }


def _run_edf_fallback(params: dict) -> dict:
    edf_path = require_path(params["edf_path"], "EDF file")
    output = io.StringIO()

    with contextlib.redirect_stdout(output):
        raw = edf_loader.load_edf_file(str(edf_path))
        start_time = edf_loader.extract_start_time(raw)
        y_pred, _, confidence = yasa_engine.run_yasa_sleep_staging(
            raw,
            eeg_name=params["eeg"].strip() or "C4:M1",
            eog_name=params["eog"].strip() or "E1:M2",
            emg_name=params["emg"].strip() or "EMG1",
            metadata=None,
        )
        infant_stages = infant_mapper.map_yasa_hypnogram_to_infant(
            y_pred,
            confidence=confidence,
            use_movement=params.get("use_movement", False),
        )
        infant_stage_ints = infant_mapper.infant_hypnogram_as_int(infant_stages)

    if start_time is not None:
        epoch_times = [start_time + datetime.timedelta(seconds=30 * i) for i in range(len(infant_stage_ints))]
    else:
        epoch_times = list(range(len(infant_stage_ints)))

    infant_counts = infant_stages.value_counts().rename_axis("stage").reset_index(name="epochs")
    raw_counts = pd.Series(y_pred).value_counts().rename_axis("stage").reset_index(name="epochs")
    preview = pd.DataFrame({"raw_stage": list(y_pred[:20])})

    return {
        "message": output.getvalue() + "\nEDF fallback staging complete. No files were written.",
        "tables": [
            {"title": "Infant Stage Counts", "data": infant_counts},
            {"title": "Raw YASA Stage Counts", "data": raw_counts},
            {"title": "Raw Prediction Preview", "data": preview},
        ],
        "figures": [
            {
                "title": "EDF Infant Hypnogram",
                "kind": "sleep_edf_hypnogram",
                "times": epoch_times,
                "values": infant_stage_ints,
            }
        ],
    }


def render_sleep_plot(canvas, spec: dict) -> None:
    ax = canvas.reset()
    if spec["kind"] == "sleep_text_profile":
        stages = list(dict.fromkeys(spec["stages"]))
        mapping = {stage: idx for idx, stage in enumerate(stages)}
        y_values = [mapping[stage] for stage in spec["stages"]]
        ax.plot(spec["timestamps"], y_values, marker="o", linewidth=1)
        ax.set_yticks(list(mapping.values()))
        ax.set_yticklabels(list(mapping.keys()))
        ax.set_title("Sleep Profile")
        ax.set_xlabel("Time")
        ax.set_ylabel("Stage")
    else:
        ax.step(spec["times"], spec["values"], where="post")
        ax.set_yticks([1, 2, 3, 4, 5])
        ax.set_yticklabels(["Wake", "Movement", "Transitional", "NREM", "REM"])
        ax.set_title("Infant-Oriented Hypnogram")
        ax.set_xlabel("Epoch")
        ax.set_ylabel("Stage")

    ax.grid(True, alpha=0.3)
    canvas.figure.autofmt_xdate()
    canvas.draw_idle()
