from __future__ import annotations

import contextlib
import io

import pandas as pd

from app.path_utils import load_module, require_path


h5_loader = load_module("app_movement_h5_loader", "movement_analysis/src/core/h5_loader.py")
acceleration_magnitude = load_module(
    "app_movement_acceleration_magnitude",
    "movement_analysis/src/core/acceleration_magnitude.py",
)
raw_acceleration = load_module("app_movement_raw_acceleration", "movement_analysis/src/core/raw_acceleration.py")
coefficient_of_variation = load_module(
    "app_movement_coefficient_of_variation",
    "movement_analysis/src/core/coefficient_of_variation.py",
)
velocity = load_module("app_movement_velocity", "movement_analysis/src/core/velocity.py")
speed = load_module("app_movement_speed", "movement_analysis/src/core/speed.py")
skewness = load_module("app_movement_skewness", "movement_analysis/src/core/skewness.py")
bowley_skew = load_module("app_movement_bowley_skew", "movement_analysis/src/core/bowley_skew.py")
zero_crossing_rate = load_module(
    "app_movement_zero_crossing_rate",
    "movement_analysis/src/core/zero_crossing_rate.py",
)


METRICS = [
    "Raw Acceleration",
    "Acceleration Magnitude",
    "Velocity",
    "Speed",
    "Coefficient of Variation",
    "Skewness",
    "Bowley-Galton Skewness",
    "Zero-Crossing Rate",
]


def run_movement_analysis(params: dict) -> dict:
    h5_path = require_path(params["h5_path"], "H5 file")
    sensor_id = params["sensor_id"].strip()
    if not sensor_id:
        raise ValueError("Sensor ID is required.")

    metric = params["metric"]
    step = int(params.get("step") or 500)
    output = io.StringIO()

    with contextlib.redirect_stdout(output):
        acc_data, time_raw, time_dt = h5_loader.load_accelerometer_data(str(h5_path), sensor_id)

        if metric == "Raw Acceleration":
            time_sampled, acc_sampled = raw_acceleration.downsample_accelerometer_data(
                acc_data,
                time_dt,
                step=step,
            )
            result_df = raw_acceleration.create_raw_accel_dataframe(time_sampled, acc_sampled)
            figure = {
                "title": "Raw Acceleration",
                "kind": "movement_raw",
                "time": time_sampled,
                "acc": acc_sampled,
                "sensor_id": sensor_id,
            }
        elif metric == "Acceleration Magnitude":
            mag_df = acceleration_magnitude.compute_acceleration_magnitude(acc_data, time_dt)
            result_df = acceleration_magnitude.compute_epoch_features(mag_df)
            figure = {"title": metric, "kind": "movement_epoch_band", "data": result_df, "y_label": "Acceleration Magnitude"}
        elif metric == "Velocity":
            result_df = velocity.calculate_velocity_stats_df(acc_data, time_dt)
            figure = {"title": metric, "kind": "movement_velocity", "data": result_df}
        elif metric == "Speed":
            result_df = speed.calculate_speed_stats_df(acc_data, time_raw, time_dt)
            figure = {"title": metric, "kind": "movement_epoch_band", "data": result_df, "y_label": "Estimated Speed"}
        elif metric == "Coefficient of Variation":
            result_df = coefficient_of_variation.calculate_cov_df(acc_data, time_dt)
            figure = {"title": metric, "kind": "movement_single", "data": result_df, "column": "cov", "y_label": "CoV"}
        elif metric == "Skewness":
            result_df = skewness.calculate_skewness_df(acc_data, time_dt)
            figure = {"title": metric, "kind": "movement_single", "data": result_df, "column": "skewness", "y_label": "Skewness"}
        elif metric == "Bowley-Galton Skewness":
            result_df = bowley_skew.calculate_bowley_skew_df(acc_data, time_dt)
            figure = {
                "title": metric,
                "kind": "movement_single",
                "data": result_df,
                "column": "bowley_skew",
                "y_label": "Bowley Skewness",
            }
        elif metric == "Zero-Crossing Rate":
            result_df = zero_crossing_rate.calculate_zcr_df(acc_data, time_dt)
            figure = {
                "title": metric,
                "kind": "movement_single",
                "data": result_df,
                "column": "zero_crossing_rate",
                "y_label": "Zero-Crossing Count",
            }
        else:
            raise ValueError(f"Unsupported movement metric: {metric}")

    describe_df = result_df.describe().reset_index() if hasattr(result_df, "describe") else pd.DataFrame()
    message = output.getvalue()
    message += f"\n{metric} complete. Showing results in the app; no CSV or image files were written."

    return {
        "message": message,
        "tables": [
            {"title": "Results", "data": result_df},
            {"title": "Summary", "data": describe_df},
        ],
        "figures": [figure],
    }


def render_movement_plot(canvas, spec: dict) -> None:
    ax = canvas.reset()
    kind = spec["kind"]

    if kind == "movement_raw":
        ax.plot(spec["time"], spec["acc"][:, 0], label="X")
        ax.plot(spec["time"], spec["acc"][:, 1], label="Y")
        ax.plot(spec["time"], spec["acc"][:, 2], label="Z")
        ax.set_ylabel("Acceleration")
        ax.set_title(f"Raw Acceleration - Sensor {spec['sensor_id']}")
    elif kind == "movement_epoch_band":
        data = spec["data"]
        ax.plot(data.index, data["mean"], label="Mean")
        if "std" in data.columns:
            ax.fill_between(data.index, data["mean"] - data["std"], data["mean"] + data["std"], alpha=0.25, label="Std Dev")
        elif {"min", "max"}.issubset(data.columns):
            ax.fill_between(data.index, data["min"], data["max"], alpha=0.25, label="Min-Max")
        ax.set_ylabel(spec["y_label"])
        ax.set_title(spec["title"])
    elif kind == "movement_velocity":
        data = spec["data"]
        for column, label in [("vx_mean", "Velocity X"), ("vy_mean", "Velocity Y"), ("vz_mean", "Velocity Z")]:
            if column in data.columns:
                ax.plot(data.index, data[column], label=label)
        ax.set_ylabel("Estimated Velocity")
        ax.set_title("Mean Estimated Velocity Components")
    else:
        data = spec["data"]
        ax.plot(data.index, data[spec["column"]], marker="o", markersize=3, label=spec["y_label"])
        ax.set_ylabel(spec["y_label"])
        ax.set_title(spec["title"])

    ax.set_xlabel("Time")
    ax.grid(True, alpha=0.3)
    ax.legend()
    canvas.figure.autofmt_xdate()
    canvas.draw_idle()
