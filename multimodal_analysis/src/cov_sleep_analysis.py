import argparse
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime, re, h5py, numpy as np
from scipy.signal import butter, filtfilt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from pathlib import Path


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
        raise ValueError(f"Recording date not found in sleep file: {sleep_file}")

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


def load_acc_df(h5_file, target_id):
    with h5py.File(h5_file, "r") as f:
        if "Sensors" not in f:
            raise KeyError(f"Missing 'Sensors' group in {h5_file}")

        sensors = f["Sensors"]
        base_key = str(target_id)
        if base_key not in sensors:
            keys = list(sensors.keys())
            if len(keys) == 1:
                base_key = keys[0]
                print(f"[warn] target_id '{target_id}' not found; using only sensor id '{base_key}'")
            else:
                raise KeyError(f"target_id '{target_id}' not found. Available: {keys}")

        base = sensors[base_key]
        if "Accelerometer" not in base or "Time" not in base:
            raise KeyError(f"Missing Accelerometer or Time in Sensors/{base_key}")

        acc_data = np.array(base["Accelerometer"][:], dtype=np.float64)
        time_raw = np.array(base["Time"][:], dtype=np.float64)
        time_dt = np.array([datetime.datetime.fromtimestamp(t * 1e-6) for t in time_raw])

    acc_df = pd.DataFrame(acc_data, columns=["ax", "ay", "az"], index=pd.to_datetime(time_dt))

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


def main():
    parser = argparse.ArgumentParser(description="CoV + Sleep multimodal analysis")
    parser.add_argument("--h5", required=True, help="Path to H5 movement file")
    parser.add_argument("--sleep", required=True, help="Path to sleep profile text file")
    parser.add_argument("--target-id", required=True, help="Sensor target ID (e.g., 16162 or XI-016162)")
    parser.add_argument("--label", default="", help="Optional label for titles")
    args = parser.parse_args()

    h5_path = Path(args.h5)
    sleep_path = Path(args.sleep)
    if not h5_path.exists():
        raise FileNotFoundError(f"H5 file not found: {h5_path}")
    if not sleep_path.exists():
        raise FileNotFoundError(f"Sleep file not found: {sleep_path}")

    sleep_df, sleep_start_dt = load_sleep_df(sleep_path)
    acc_df = load_acc_df(h5_path, args.target_id)
    cov_30s = cov_30s_from_acc(acc_df)

    plot1_states = ["wake", "nrem", "rem", "transitional", "movement", "a"]
    plot1_colors = {
        "wake": "#ff8c00",
        "nrem": "#1f77b4",
        "rem": "#2ca02c",
        "transitional": "#9467bd",
        "movement": "#8c564b",
        "a": "#7f7f7f",
    }

    sleep_states = ["nrem", "rem", "transitional"]
    sleep_colors = {"nrem": "#1f77b4", "rem": "#2ca02c", "transitional": "#9467bd"}

    plot1_df = sleep_df[sleep_df["state_norm"].isin(plot1_states)]
    sleep_only_df = sleep_df[sleep_df["state_norm"].isin(sleep_states)]

    print("\n=== BASIC STATS ===")
    print(cov_30s.describe())

    # ---- Plot 1: full timeline
    fig, ax = plt.subplots(figsize=(15, 7))
    ax.plot(cov_30s.index, cov_30s.values, color="magenta", lw=1.5)

    epoch = cov_30s.index.to_series().diff().median()
    if pd.isna(epoch) or epoch <= pd.Timedelta(0):
        epoch = pd.Timedelta(seconds=30)
    half = epoch / 2

    for state, color in plot1_colors.items():
        sdf = plot1_df[plot1_df["state_norm"] == state].copy()
        sdf["gap"] = (sdf.index.to_series().diff() > pd.Timedelta("40s")).cumsum()
        for _, blk in sdf.groupby("gap"):
            left = blk.index.min() - half
            right = blk.index.max() + half
            ax.axvspan(left, right, color=color, alpha=0.25, linewidth=0)

    legend1 = (
        [Patch(facecolor=c, edgecolor="none", alpha=0.25, label=s.upper()) for s, c in plot1_colors.items()]
        + [Line2D([0], [0], color="magenta", lw=1.5, label="CoV")]
    )
    ax.legend(handles=legend1, loc="upper right")
    title_label = f" - {args.label}" if args.label else ""
    ax.set_title(f"Continuous Movement Variability (CoV){title_label}")
    ax.set_xlabel("Time")
    ax.set_ylabel("Coefficient of Variation")
    ax.grid(True)
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=6, maxticks=10))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    plt.tight_layout()
    plt.show()

    # ---- Plot 2: compressed sleep-only
    fig2, ax2 = plt.subplots(figsize=(15, 7))

    sleep_labels = sleep_only_df["state"].reindex(
        cov_30s.index, method="nearest", tolerance=pd.Timedelta("40s")
    )
    sleep_mask = sleep_labels.str.lower().isin(sleep_states)
    sleep_cov = cov_30s[sleep_mask].copy()
    sleep_state_for_cov = sleep_labels[sleep_mask].str.lower()

    df_blocks = pd.DataFrame({"state": sleep_state_for_cov, "original_time": sleep_cov.index})
    df_blocks["time_diff"] = df_blocks["original_time"].diff()
    df_blocks["block_id"] = (
        (df_blocks["state"] != df_blocks["state"].shift())
        | (df_blocks["time_diff"] > pd.Timedelta("40s"))
    ).cumsum()

    time_mapping = {}
    current_time = pd.Timedelta(0)

    for block_id in sorted(df_blocks["block_id"].unique()):
        group = df_blocks[df_blocks["block_id"] == block_id]
        block_start = group["original_time"].min()
        block_duration = group["original_time"].max() - block_start + pd.Timedelta("30s")

        for t in group["original_time"]:
            time_mapping[t] = current_time + (t - block_start)

        current_time += block_duration

    compressed_times = [time_mapping[t] for t in sleep_cov.index]
    sleep_cov_compressed = sleep_cov.copy()
    sleep_cov_compressed.index = pd.to_datetime(sleep_start_dt) + pd.to_timedelta(compressed_times)

    ax2.plot(sleep_cov_compressed.index, sleep_cov_compressed.values, color="magenta", lw=1.5)

    for state in sleep_states:
        mask = sleep_state_for_cov == state
        if mask.any():
            idx = sleep_cov_compressed.index[mask]
            ax2.axvspan(idx.min(), idx.max(), color=sleep_colors[state], alpha=0.25)

    legend2 = (
        [Patch(facecolor=c, alpha=0.25, label=s.upper()) for s, c in sleep_colors.items()]
        + [Patch(facecolor="magenta", alpha=0.5, label="CoV")]
    )
    ax2.legend(handles=legend2, loc="upper right")
    ax2.set_title(f"Compressed Sleep CoV{title_label}")
    ax2.set_xlabel("Compressed Sleep Time")
    ax2.set_ylabel("Coefficient of Variation")
    ax2.grid(True)
    ax2.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=6, maxticks=10))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
