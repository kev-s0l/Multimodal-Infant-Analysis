import argparse
import os
from src.core.zcr_core import compute_zcr_stats

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute ZCR (30s epochs) from H5")
    parser.add_argument("h5_path", help="Path to H5 file")
    parser.add_argument("target_id", help="Sensor ID (e.g., 16162)")
    parser.add_argument("--out", default="movement_outputs", help="Output folder")
    args = parser.parse_args()

    zcr_df = compute_zcr_stats(args.h5_path, args.target_id)

    print("\n--- Zero-Crossing Rate of Motion Change (30s Epochs) ---")
    print(zcr_df.head())

    os.makedirs(args.out, exist_ok=True)

    base = os.path.splitext(os.path.basename(args.h5_path))[0]
    out_csv = os.path.join(args.out, f"{base}_zcr.csv")

    zcr_df.to_csv(out_csv)
    print(f"\nSaved ZCR data to {out_csv}")
