import pandas as pd


def calculate_daily_totals(recording_info, segments, conversations):

    recording_start = pd.to_datetime(
        recording_info["start_clock_time"].iloc[0]
    )

    segments["time_offset"] = pd.to_timedelta(
        segments["start_time"], errors="coerce"
    )

    segments["absolute_time"] = segments["time_offset"].apply(
        lambda x: recording_start + x
    )

    segments["date"] = segments["absolute_time"].dt.date

    segments["AWC"] = (
        segments["fem_adult_word_cnt"].fillna(0) +
        segments["male_adult_word_cnt"].fillna(0)
    )

    daily_awc_cvc = (
        segments.groupby("date")
        .agg(AWC=("AWC", "sum"),
             CVC=("child_utt_count", "sum"))
        .reset_index()
    )

    conversations["time_offset"] = pd.to_timedelta(
        conversations["start_time"], errors="coerce"
    )

    conversations["absolute_time"] = conversations["time_offset"].apply(
        lambda x: recording_start + x
    )

    conversations["date"] = conversations["absolute_time"].dt.date

    daily_ctc = (
        conversations.groupby("date")
        .agg(CTC=("turn_count", "sum"))
        .reset_index()
    )

    summary = pd.merge(
        daily_awc_cvc,
        daily_ctc,
        on="date",
        how="outer"
    ).fillna(0)

    return summary