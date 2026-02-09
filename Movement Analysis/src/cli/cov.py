import argparse
import os
from src.core.cov_core import compute_cov_stats

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute CoV (30s epochs) from H5")
    parser.add_argument("h5_path", help="Path to H5 file")
    parser.add_argument("target_id", help="Sensor ID (e.g., 16162 or XI-016162)")
    parser.add_argument("--out", default="movement_outputs", help="Output folder")
    args = parser.parse_args()

    cov_df = compute_cov_stats(args.h5_path, args.target_id)

    print("\n--- Coefficient of Variation (CoV) per 30s Epoch ---")
    print(cov_df.head())

    os.makedirs(args.out, exist_ok=True)

    base = os.path.splitext(os.path.basename(args.h5_path))[0]
    out_csv = os.path.join(args.out, f"{base}_cov.csv")

    cov_df.to_csv(out_csv)
    print(f"\nSaved CoV data to {out_csv}")
