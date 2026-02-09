# src/core/sleep_profile_core.py
from datetime import datetime
import pandas as pd

STAGE_VALUES = {
    "Wake": 4,
    "Movement": 3,
    "Transitional": 2,
    "NREM": 1,
    "REM": 0,
}

def parse_sleep_profile(txt_path):
    sleep_stages = []
    timestamps = []

    with open(txt_path, "r") as f:
        lines = f.readlines()

    data_start = 0
    for i, line in enumerate(lines):
        if ";" in line and "," in line and ":" in line.split(";")[0]:
            data_start = i
            break

    for line in lines[data_start:]:
        line = line.strip()
        if not line or ";" not in line:
            continue
        try:
            time_str, stage = [part.strip() for part in line.split(";")[:2]]
            if stage == "A":
                continue
            time_obj = datetime.strptime(time_str.split(",")[0], "%H:%M:%S")
            timestamps.append(time_obj)
            sleep_stages.append(stage)
        except Exception:
            continue

    if not timestamps:
        raise ValueError("No valid timestamps found in sleep profile.")

    df = pd.DataFrame({
        "time": timestamps,
        "stage": sleep_stages
    })
    df["stage_code"] = df["stage"].map(STAGE_VALUES)

    # ---- Stats ----
    counts = df["stage"].value_counts()
    total_epochs = len(df)

    stage_minutes = {stage: cnt * 0.5 for stage, cnt in counts.items()}
    stage_percentages = {stage: (cnt / total_epochs) * 100 for stage, cnt in counts.items()}

    summary = {
        "total_epochs": total_epochs,
        "stage_minutes": stage_minutes,
        "stage_percentages": stage_percentages,
    }

    return df, summary
