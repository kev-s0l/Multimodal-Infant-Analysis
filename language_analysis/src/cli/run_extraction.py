import argparse
import pandas as pd
import os
from core.its_loader import parse_file, extract_recording_info
from core.its_extraction import extract_segments, extract_conversations
from core.statistics import calculate_summary_stats, create_hourly_analysis

def main():
    parser = argparse.ArgumentParser(
        description="Run LENA ITS extraction pipeline"
    )

    parser.add_argument(
        "--its",
        required=True,
        help="Path to the ITS file"
    )

    args = parser.parse_args()
    its_file_path = args.its

    result = parse_file(its_file_path)
    if not result:
        return

    tree, root = result 

    recording_info = extract_recording_info(root, its_file_path)
    segments = extract_segments(root)
    conversations = extract_conversations(root)
    summary_stats = calculate_summary_stats(segments, conversations)
    hourly_analysis = create_hourly_analysis(segments)

    output_dir = "lena_extraction_output"
    os.makedirs(output_dir, exist_ok=True)

    pd.DataFrame([recording_info]).to_csv(
        os.path.join(output_dir, "recording_info.csv"),
        index=False
    )

    pd.DataFrame(segments).to_csv(
        os.path.join(output_dir, "segments.csv"),
        index=False
    )

    pd.DataFrame(conversations).to_csv(
        os.path.join(output_dir, "conversations.csv"),
        index=False
    )

    pd.DataFrame([summary_stats]).to_csv(
        os.path.join(output_dir, "summary_statistics.csv"),
        index=False
    )

    if not hourly_analysis.empty:
        hourly_analysis.to_csv(
            os.path.join(output_dir, "hourly_analysis.csv"),
            index=False
        )


    print("\nExtraction complete!")
    print(f"Segments extracted: {len(segments)}")
    print(f"Conversations extracted: {len(conversations)}")
    print(summary_stats)



if __name__ == "__main__":
    main()