from __future__ import annotations

import contextlib
import io

import pandas as pd

from app.path_utils import load_module, require_path


its_loader = load_module("app_language_its_loader", "language_analysis/src/core/its_loader.py")
its_extraction = load_module("app_language_its_extraction", "language_analysis/src/core/its_extraction.py")
statistics = load_module("app_language_statistics", "language_analysis/src/core/statistics.py")
daily_summary = load_module("app_language_daily_summary", "language_analysis/src/core/daily_summary.py")


def run_language_analysis(params: dict) -> dict:
    its_path = require_path(params["its_path"], "ITS file")
    output = io.StringIO()

    with contextlib.redirect_stdout(output):
        parsed = its_loader.parse_file(str(its_path))
        if not parsed:
            raise ValueError("Could not parse ITS file.")

        _, root = parsed
        recording_info = its_loader.extract_recording_info(root, str(its_path))
        segments = its_extraction.extract_segments(root)
        conversations = its_extraction.extract_conversations(root)
        summary_stats = statistics.calculate_summary_stats(segments, conversations)
        hourly = statistics.create_hourly_analysis(segments)

    recording_df = pd.DataFrame([recording_info])
    segments_df = pd.DataFrame(segments)
    conversations_df = pd.DataFrame(conversations)
    summary_df = pd.DataFrame([summary_stats])

    tables = [
        {"title": "Summary Statistics", "data": summary_df},
        {"title": "Recording Info", "data": recording_df},
        {"title": "Hourly Analysis", "data": hourly},
        {"title": "Segments", "data": segments_df},
        {"title": "Conversations", "data": conversations_df},
    ]

    figures = []
    if not segments_df.empty and not conversations_df.empty:
        try:
            daily = daily_summary.calculate_daily_totals(
                recording_df.copy(),
                segments_df.copy(),
                conversations_df.copy(),
            )
            tables.insert(2, {"title": "Daily Summary", "data": daily})
            figures.append({"title": "Daily AWC CVC CTC", "kind": "language_daily", "data": daily})
        except Exception as exc:
            output.write(f"\nDaily summary could not be created: {exc}\n")

    return {
        "message": output.getvalue() or "Language analysis complete.",
        "tables": tables,
        "figures": figures,
    }


def render_language_plot(canvas, spec: dict) -> None:
    ax = canvas.reset()
    daily = spec["data"]
    if daily.empty:
        canvas.draw_idle()
        return

    x = daily["date"].astype(str)
    ax.plot(x, daily["AWC"], marker="o", label="AWC")
    ax.plot(x, daily["CVC"], marker="o", label="CVC")
    ax.plot(x, daily["CTC"], marker="o", label="CTC")
    ax.set_title("Daily Language Summary")
    ax.set_xlabel("Date")
    ax.set_ylabel("Count")
    ax.tick_params(axis="x", rotation=30)
    ax.grid(True, alpha=0.3)
    ax.legend()
    canvas.draw_idle()
