import pandas as pd

def calculate_summary_stats(segments, conversations):
    if not segments:
        print("No segments available")
        return {}

    df = pd.DataFrame(segments)

    numeric_cols = [
        "child_utt_count",
        "child_utt_len",
        "fem_adult_word_cnt",
        "male_adult_word_cnt",
        "fem_adult_utt_cnt",
        "male_adult_utt_cnt",
        "overlap_cnt",
        "duration_seconds",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    summary = {
        "total_recording_time_seconds": df["duration_seconds"].sum(),
        "total_segments": len(df),

        "adult_word_count_total":
            df["fem_adult_word_cnt"].sum() +
            df["male_adult_word_cnt"].sum(),

        "child_vocalization_count":
            df["child_utt_count"].sum(),

        "adult_utterance_total":
            df["fem_adult_utt_cnt"].sum() +
            df["male_adult_utt_cnt"].sum(),

        "total_conversations": len(conversations),

        "total_turn_count":
            sum(int(c["turn_count"]) for c in conversations
                if str(c["turn_count"]).isdigit()),
    }

    return summary

def create_hourly_analysis(segments):
    if not segments:
        return pd.DataFrame()

    df = pd.DataFrame(segments)

    df["start_time"] = pd.to_numeric(df["start_time"], errors="coerce").fillna(0)

    df["hour"] = (df["start_time"] / (1000 * 60 * 60)).astype(int)

    hourly = df.groupby("hour").agg(
        fem_adult_word_cnt=("fem_adult_word_cnt", "sum"),
        male_adult_word_cnt=("male_adult_word_cnt", "sum"),
        child_utt_count=("child_utt_count", "sum"),
        duration_seconds=("duration_seconds", "sum"),
    ).reset_index()

    hourly["total_adult_words"] = (
        hourly["fem_adult_word_cnt"] +
        hourly["male_adult_word_cnt"]
    )

    return hourly