import argparse
import datetime
import re
from pathlib import Path

import h5py
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt


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
            file_date = datetime.datetime.strptime(name_match.group(1), "%Y%m%d").date()

    if file_date is None:
        raise ValueError(f"Recording date not found for sleep file: {sleep_file}")

    return datetime.datetime.combine(file_date, start_clock_time or datetime.time(0, 0, 0))


def load_sleep_df(sleep_file):
    sleep_start_dt = parse_sleep_start(sleep_file)
    sleep_data = []

    with open(sleep_file, "r", errors="ignore") as f:
        for line in f:
            if ";" not in line:
                continue
            time_part, state = line.strip().split(";")
            try:
                time_obj = datetime.datetime.strptime(time_part.strip(), "%H:%M:%S,%f").time()
                full_time = datetime.datetime.combine(sleep_start_dt.date(), time_obj)
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


def butter_lowpass_filter(data, cutoff=3, fs=50, order=4):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype="low")
    return filtfilt(b, a, data)


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
                print(f"[warn] target_id '{target_id}' not found; using only sensor id '{base_key}' in {h5_file}")
            else:
                raise KeyError(
                    f"target_id '{target_id}' not found. Available sensor ids in {h5_file}: {sensor_keys}"
                )

        base_group = sensors[base_key]
        acc_path = "Accelerometer"
        time_path = "Time"

        if acc_path not in base_group:
            acc_candidates = [k for k in _list_group_keys(base_group) if "accelerometer" in k.lower()]
            acc_path = _pick_single_or_error(acc_candidates, "Accelerometer dataset", f"Sensors/{base_key}")

        if time_path not in base_group:
            time_candidates = [k for k in _list_group_keys(base_group) if k.lower() == "time" or "time" in k.lower()]
            time_path = _pick_single_or_error(time_candidates, "Time dataset", f"Sensors/{base_key}")

        acc_data = np.array(base_group[acc_path][:], dtype=np.float64)
        time_raw = np.array(base_group[time_path][:], dtype=np.float64)
        time_dt = np.array([datetime.datetime.fromtimestamp(t * 1e-6) for t in time_raw])

    acc_df = pd.DataFrame(
        acc_data,
        columns=["ax", "ay", "az"],
        index=pd.to_datetime(time_dt),
    )

    acc_df["mag"] = np.sqrt(acc_df["ax"] ** 2 + acc_df["ay"] ** 2 + acc_df["az"] ** 2)
    acc_df["mag"] = acc_df["mag"].clip(
        lower=acc_df["mag"].quantile(0.01),
        upper=acc_df["mag"].quantile(0.99),
    )
    acc_df["mag"] -= acc_df["mag"].rolling(window=250, center=True, min_periods=1).mean()
    acc_df["mag"] = butter_lowpass_filter(acc_df["mag"].interpolate(), cutoff=3, fs=50)
    acc_df.dropna(inplace=True)
    return acc_df


def cov_30s_from_acc(acc_df):
    def cov_func(x):
        mean_x = x.mean()
        return np.nan if mean_x == 0 else x.std() / mean_x

    return acc_df["mag"].resample("30s").apply(cov_func).dropna()


def summarize_subject(cov_30s, sleep_df):
    stats = {
        "cov_mean": cov_30s.mean(),
        "cov_median": cov_30s.median(),
        "cov_std": cov_30s.std(),
        "cov_var": cov_30s.var(),
        "cov_min": cov_30s.min(),
        "cov_max": cov_30s.max(),
        "cov_p05": cov_30s.quantile(0.05),
        "cov_p25": cov_30s.quantile(0.25),
        "cov_p75": cov_30s.quantile(0.75),
        "cov_p95": cov_30s.quantile(0.95),
    }

    sleep_states = ["nrem", "rem", "transitional"]
    sleep_only_df = sleep_df[sleep_df["state_norm"].isin(sleep_states)]

    sleep_start = sleep_only_df.index.min()
    sleep_end = sleep_only_df.index.max()
    total_sleep_seconds = (sleep_end - sleep_start).total_seconds() if pd.notna(sleep_start) else 0
    total_record_seconds = (cov_30s.index[-1] - cov_30s.index[0]).total_seconds()

    stats["total_sleep_hours"] = total_sleep_seconds / 3600.0
    stats["total_record_hours"] = total_record_seconds / 3600.0
    stats["sleep_efficiency_pct"] = (
        (total_sleep_seconds / total_record_seconds) * 100.0 if total_record_seconds > 0 else np.nan
    )

    hi_thr = cov_30s.quantile(0.95)
    hi_mask = cov_30s > hi_thr
    hi_blocks = hi_mask.astype(int).diff().fillna(0).ne(0).cumsum()
    hi_groups = cov_30s[hi_mask].groupby(hi_blocks[hi_mask])

    if hi_mask.any():
        burst_durations = []
        burst_peaks = []
        for _, g in hi_groups:
            duration_s = len(g) * 30
            burst_durations.append(duration_s)
            burst_peaks.append(g.max())
        stats["burst_count"] = len(burst_durations)
        stats["burst_total_min"] = sum(burst_durations) / 60.0
        stats["burst_mean_s"] = float(np.mean(burst_durations))
        stats["burst_max_s"] = float(np.max(burst_durations))
        stats["burst_peak_cov"] = float(np.max(burst_peaks))
    else:
        stats["burst_count"] = 0
        stats["burst_total_min"] = 0.0
        stats["burst_mean_s"] = 0.0
        stats["burst_max_s"] = 0.0
        stats["burst_peak_cov"] = np.nan

    return stats


def pairwise_comparison(df, id_cols):
    numeric_cols = [c for c in df.columns if c not in id_cols]
    rows = []

    for pair_id, group in df.groupby("pair_id"):
        if len(group) != 2:
            continue
        a, b = group.iloc[0], group.iloc[1]
        for col in numeric_cols:
            a_val = a[col]
            b_val = b[col]
            diff = b_val - a_val
            pct = (diff / a_val) * 100.0 if pd.notna(a_val) and a_val != 0 else np.nan
            rows.append(
                {
                    "pair_id": pair_id,
                    "metric": col,
                    "subject_a": a["subject_label"],
                    "subject_b": b["subject_label"],
                    "a_value": a_val,
                    "b_value": b_val,
                    "diff_b_minus_a": diff,
                    "pct_diff": pct,
                }
            )

    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(description="Compare CoV summary stats across subject pairs.")
    parser.add_argument("--manifest", required=True, help="CSV with pair_id,subject_label,h5_path,sleep_path,target_id.")
    parser.add_argument("--out-dir", default="reports", help="Output directory for CSV reports.")
    args = parser.parse_args()

    manifest = pd.read_csv(args.manifest)
    required_cols = {"pair_id", "subject_label", "h5_path", "sleep_path", "target_id"}
    missing = required_cols - set(manifest.columns)
    if missing:
        raise ValueError(f"Manifest missing columns: {sorted(missing)}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for _, row in manifest.iterrows():
        pair_id = row["pair_id"]
        subject_label = row["subject_label"]
        h5_path = row["h5_path"]
        sleep_path = row["sleep_path"]
        target_id = row["target_id"]

        sleep_df, _ = load_sleep_df(sleep_path)
        acc_df = load_acc_df(h5_path, target_id)
        cov_30s = cov_30s_from_acc(acc_df)
        stats = summarize_subject(cov_30s, sleep_df)

        rows.append(
            {
                "pair_id": pair_id,
                "subject_label": subject_label,
                "h5_path": h5_path,
                "sleep_path": sleep_path,
                "target_id": target_id,
                **stats,
            }
        )

    summary_df = pd.DataFrame(rows)
    summary_path = out_dir / "subject_summary.csv"
    summary_df.to_csv(summary_path, index=False)

    compare_df = pairwise_comparison(summary_df, id_cols=["pair_id", "subject_label", "h5_path", "sleep_path", "target_id"])
    compare_path = out_dir / "pair_comparison.csv"
    compare_df.to_csv(compare_path, index=False)

    print(f"Wrote: {summary_path}")
    print(f"Wrote: {compare_path}")


if __name__ == "__main__":
    main()
