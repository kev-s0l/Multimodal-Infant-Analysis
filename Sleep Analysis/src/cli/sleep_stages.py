# src/cli/sleep_stages.py
import argparse
import os
from src.core.sleep_stages_core import compute_sleep_stages_from_edf

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute sleep stages from EDF")
    parser.add_argument("edf_path", help="Path to EDF file")
    parser.add_argument("--out", default="sleep_outputs", help="Output folder")
    args = parser.parse_args()

    df, summary, start_time = compute_sleep_stages_from_edf(args.edf_path)

    print("\n--- Infant EEG Sleep Stage Summary ---")
    print(f"Recording Duration: {summary['total_hours']:.2f} hours")
    print("Sleep Stage Distribution (%):")
    for k, v in summary.items():
        if k.endswith("_percent"):
            stage = k.replace("_percent", "")
            print(f" - {stage:12}: {v:.2f}%")

    os.makedirs(args.out, exist_ok=True)
    out_csv = os.path.join(args.out, "sleep_stages.csv")
    df.to_csv(out_csv, index=False)
    print(f"\nSaved sleep stages to: {out_csv}")
    