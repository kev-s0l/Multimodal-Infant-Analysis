import argparse
import os
from src.core.skew_core import compute_bowley_skew

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute Bowley-Galton skewness (30s epochs) from H5")
    parser.add_argument("h5_path", help="Path to H5 file")
    parser.add_argument("target_id", help="Sensor ID (e.g., 16162 or XI-016162)")
    parser.add_argument("--out", default="movement_outputs", help="Output folder")
    args = parser.parse_args()

    skew_df = compute_bowley_skew(args.h5_path, args.target_id)

    print("\n--- Bowley-Galton Skewness of Acceleration Magnitude (30s Epochs) ---")
    print(skew_df.head())

    os.makedirs(args.out, exist_ok=True)

    base = os.path.splitext(os.path.basename(args.h5_path))[0]
    out_csv = os.path.join(args.out, f"{base}_bowley_skew.csv")

    skew_df.to_csv(out_csv)
    print(f"\nSaved skewness data to {out_csv}")
