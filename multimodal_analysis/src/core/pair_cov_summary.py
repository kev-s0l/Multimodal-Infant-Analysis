import numpy as np
import pandas as pd


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
    total_sleep_seconds = (
        (sleep_end - sleep_start).total_seconds()
        if pd.notna(sleep_start) else 0
    )
    total_record_seconds = (
        cov_30s.index[-1] - cov_30s.index[0]
    ).total_seconds()

    stats["total_sleep_hours"] = total_sleep_seconds / 3600.0
    stats["total_record_hours"] = total_record_seconds / 3600.0
    stats["sleep_efficiency_pct"] = (
        (total_sleep_seconds / total_record_seconds) * 100.0
        if total_record_seconds > 0 else np.nan
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
            pct = (
                (diff / a_val) * 100.0
                if pd.notna(a_val) and a_val != 0
                else np.nan
            )

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