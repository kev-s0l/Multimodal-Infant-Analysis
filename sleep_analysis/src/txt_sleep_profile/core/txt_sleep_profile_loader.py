from datetime import datetime


def parse_sleep_profile(sleep_file):
    """
    Parse sleep stages and timestamps from a sleep profile text file.
    """

    sleep_stages = []
    timestamps = []

    with open(sleep_file, "r") as file:
        lines = file.readlines()

    # Skip metadata lines (header ends when line starts with timestamp-like data)
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
                continue  # Skip Artifact

            time_obj = datetime.strptime(time_str.split(",")[0], "%H:%M:%S")
            timestamps.append(time_obj)
            sleep_stages.append(stage)

        except Exception:
            continue

    if not timestamps:
        raise ValueError("No valid timestamps found in sleep profile.")

    return timestamps, sleep_stages