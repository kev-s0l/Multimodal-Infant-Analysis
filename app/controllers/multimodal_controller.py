from __future__ import annotations

import contextlib
import io

import pandas as pd

from app.path_utils import load_module, require_path


cov_sleep_loader = load_module("app_multimodal_cov_sleep_loader", "multimodal_analysis/src/core/cov_sleep_loader.py")
cov_sleep_processing = load_module(
    "app_multimodal_cov_sleep_processing",
    "multimodal_analysis/src/core/cov_sleep_processing.py",
)
cov_sleep_analysis = load_module(
    "app_multimodal_cov_sleep_analysis",
    "multimodal_analysis/src/core/cov_sleep_analysis.py",
)
pair_cov_loader = load_module("app_multimodal_pair_cov_loader", "multimodal_analysis/src/core/pair_cov_loader.py")
pair_cov_processing = load_module(
    "app_multimodal_pair_cov_processing",
    "multimodal_analysis/src/core/pair_cov_processing.py",
)
pair_cov_summary = load_module("app_multimodal_pair_cov_summary", "multimodal_analysis/src/core/pair_cov_summary.py")


def run_multimodal_analysis(params: dict) -> dict:
    mode = params["mode"]
    if mode == "CoV + Sleep":
        return _run_cov_sleep(params)
    if mode == "Pairwise CoV Comparison":
        return _run_pairwise(params)
    raise ValueError(f"Unsupported multimodal mode: {mode}")


def _run_cov_sleep(params: dict) -> dict:
    h5_path = require_path(params["h5_path"], "H5 file")
    sleep_path = require_path(params["sleep_path"], "Sleep profile")
    sensor_id = params["sensor_id"].strip()
    if not sensor_id:
        raise ValueError("Sensor ID is required.")

    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        file_date, _, sleep_start_dt = cov_sleep_loader.parse_sleep_start_info(str(sleep_path))
        sleep_df = cov_sleep_loader.load_sleep_states(str(sleep_path), file_date)
        acc_data, time_dt = cov_sleep_loader.load_accelerometer_data(str(h5_path), sensor_id)
        acc_df = cov_sleep_processing.prepare_accelerometer_dataframe(acc_data, time_dt)
        cov_30s = cov_sleep_processing.compute_cov_30s(acc_df)
        plot1_states, plot1_colors, sleep_states, sleep_colors = cov_sleep_processing.get_plot_state_config()
        cov_sleep_analysis.print_start_time_checks(acc_df, cov_30s, sleep_df)
        state_cov, hourly_cov = cov_sleep_analysis.run_analytics(
            cov_30s,
            sleep_df,
            plot1_states,
            sleep_states,
            acc_df,
        )

    cov_df = cov_30s.rename("cov").reset_index()
    cov_df.columns = ["timestamp", "cov"]
    hourly_df = hourly_cov.rename("mean_cov").reset_index()
    hourly_df.columns = ["hour", "mean_cov"]

    return {
        "message": output.getvalue() + "\nCoV + sleep analysis complete. No files were written.",
        "tables": [
            {"title": "CoV 30s", "data": cov_df},
            {"title": "State CoV", "data": state_cov.reset_index()},
            {"title": "Hourly CoV", "data": hourly_df},
        ],
        "figures": [
            {
                "title": "Continuous CoV",
                "kind": "multimodal_cov",
                "cov": cov_30s,
                "sleep_df": sleep_df,
                "states": plot1_states,
                "colors": plot1_colors,
            },
            {"title": "Hourly CoV", "kind": "multimodal_hourly", "hourly": hourly_cov},
        ],
    }


def _run_pairwise(params: dict) -> dict:
    manifest_path = require_path(params["manifest_path"], "Manifest CSV")
    manifest = pd.read_csv(manifest_path)
    required_cols = {"pair_id", "subject_label", "h5_path", "sleep_path", "target_id"}
    missing = required_cols - set(manifest.columns)
    if missing:
        raise ValueError(f"Manifest missing columns: {sorted(missing)}")

    output = io.StringIO()
    rows = []
    with contextlib.redirect_stdout(output):
        for _, row in manifest.iterrows():
            sleep_df, _ = pair_cov_loader.load_sleep_df(row["sleep_path"])
            acc_df = pair_cov_loader.load_acc_df(row["h5_path"], row["target_id"])
            acc_df = pair_cov_processing.prepare_acc_df(acc_df)
            cov_30s = pair_cov_processing.cov_30s_from_acc(acc_df)
            stats = pair_cov_summary.summarize_subject(cov_30s, sleep_df)
            rows.append(
                {
                    "pair_id": row["pair_id"],
                    "subject_label": row["subject_label"],
                    "h5_path": row["h5_path"],
                    "sleep_path": row["sleep_path"],
                    "target_id": row["target_id"],
                    **stats,
                }
            )

    summary_df = pd.DataFrame(rows)
    comparison_df = pair_cov_summary.pairwise_comparison(
        summary_df,
        id_cols=["pair_id", "subject_label", "h5_path", "sleep_path", "target_id"],
    )

    return {
        "message": output.getvalue() + "\nPairwise comparison complete. No reports were written.",
        "tables": [
            {"title": "Subject Summary", "data": summary_df},
            {"title": "Pair Comparison", "data": comparison_df},
        ],
        "figures": [
            {
                "title": "Subject Mean CoV",
                "kind": "multimodal_pair_bar",
                "summary": summary_df,
            }
        ],
    }


def render_multimodal_plot(canvas, spec: dict) -> None:
    ax = canvas.reset()
    kind = spec["kind"]

    if kind == "multimodal_cov":
        cov = spec["cov"]
        sleep_df = spec["sleep_df"]
        ax.plot(cov.index, cov.values, color="magenta", linewidth=1.2, label="CoV")
        epoch = cov.index.to_series().diff().median()
        if pd.isna(epoch) or epoch <= pd.Timedelta(0):
            epoch = pd.Timedelta(seconds=30)
        half = epoch / 2
        for state, color in spec["colors"].items():
            subset = sleep_df[sleep_df["state_norm"] == state].copy()
            if subset.empty:
                continue
            subset["gap"] = (subset.index.to_series().diff() > pd.Timedelta("40s")).cumsum()
            for _, block in subset.groupby("gap"):
                ax.axvspan(block.index.min() - half, block.index.max() + half, color=color, alpha=0.18, linewidth=0)
        ax.set_title("Continuous Movement Variability Across Sleep States")
        ax.set_xlabel("Time")
        ax.set_ylabel("Coefficient of Variation")
        ax.legend()
    elif kind == "multimodal_hourly":
        hourly = spec["hourly"]
        ax.bar(hourly.index.astype(str), hourly.values)
        ax.set_title("Hourly Mean CoV")
        ax.set_xlabel("Hour")
        ax.set_ylabel("Mean CoV")
    else:
        summary = spec["summary"]
        labels = summary["subject_label"].astype(str)
        ax.bar(labels, summary["cov_mean"])
        ax.set_title("Subject Mean CoV")
        ax.set_xlabel("Subject")
        ax.set_ylabel("Mean CoV")
        ax.tick_params(axis="x", rotation=30)

    ax.grid(True, alpha=0.3)
    canvas.figure.autofmt_xdate()
    canvas.draw_idle()
