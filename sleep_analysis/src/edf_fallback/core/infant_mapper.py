import pandas as pd
import numpy as np


def map_yasa_stage(
    stage,
    confidence=None,
    use_movement=False,
    movement_conf_threshold=0.55
):
    """
    Map a single YASA stage to an infant-oriented stage label.
    """

    stage = str(stage).upper()
    print(f"DEBUG mapped input stage: {stage}")

    if stage in ["REM", "R"]:
        return "REM"

    if stage in ["N2", "N3"]:
        return "NREM"

    if stage in ["N1", "TRANSITIONAL", "T"]:
        return "Transitional"

    if stage in ["ART", "UNS", "MOVEMENT", "M"]:
        return "Movement"

    if stage in ["WAKE", "W"]:
        if use_movement and confidence is not None and confidence < movement_conf_threshold:
            return "Movement"
        return "Wake"

    return "Movement"


def map_yasa_hypnogram_to_infant(
    y_pred,
    confidence=None,
    use_movement=False,
    movement_conf_threshold=0.55
):
    """
    Map a YASA hypnogram output to infant-oriented sleep stages.
    """

    if hasattr(y_pred, "hypno"):
        hypno_series = y_pred.hypno.copy()
    else:
        hypno_series = pd.Series(y_pred).copy()

    if confidence is None:
        confidence_values = [None] * len(hypno_series)
    else:
        confidence_values = list(confidence)

    infant_stages = [
        map_yasa_stage(
            stage,
            confidence=conf,
            use_movement=use_movement,
            movement_conf_threshold=movement_conf_threshold
        )
        for stage, conf in zip(hypno_series.astype(str), confidence_values)
    ]

    return pd.Series(
        infant_stages,
        index=hypno_series.index,
        name="InfantStage"
    )


def infant_stage_to_int(stage):
    mapping = {
        "Wake": 1,
        "Movement": 2,
        "Transitional": 3,
        "NREM": 4,
        "REM": 5,
    }
    return mapping.get(stage, np.nan)


def infant_hypnogram_as_int(infant_stages):
    return pd.Series(
        [infant_stage_to_int(stage) for stage in infant_stages],
        index=infant_stages.index,
        name="InfantStageInt"
    )