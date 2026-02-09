# src/cli/sleep_profile.py
import argparse
import os
from src.core.sleep_profile_core import parse_sleep_profile

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse Sleep profile.txt")
    parser.add_argument("txt_path", help="Path to Sleep profile.txt")
    parser.add_argument("--out", default="sleep_outputs", help="Output folder")
    args = parser.parse_args()

    df, summary = parse_sleep_profile(args.txt_path)

    print("\nSleep Statistics:")
    print("-" * 40)
    for stage in ["Wake", "Movement", "Transitional", "NREM", "REM"]:
        if stage in summary["stage_minutes"]:
            mins = summary["stage_minutes"][stage]
            pct = summary["stage_percentages"][stage]
            print(f"{stage:12}: {mins:6.1f} min ({pct:5.1f}%)")

    os.makedirs(args.out, exist_ok=True)
    out_csv = os.path.join(args.out, "sleep_profile.csv")
    df.to_csv(out_csv, index=False)
    print(f"\nSaved sleep profile to: {out_csv}")
