import argparse
import os
from src.core.magnitude_core import compute_acc_magnitude_stats

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute acceleration magnitude stats (30s epochs)")
    parser.add_argument("h5_path", help="Path to H5 file")
    parser.add_argument("target_id", help="Sensor ID (e.g., XI-016162 or 16162)")
    parser.add_argument("--out", default="movement_outputs", help="Output folder")
    args = parser.parse_args()

    epoch_features = compute_acc_magnitude_stats(args.h5_path, args.target_id)

    print("\n--- Acceleration Magnitude Statistics ---")
    print(epoch_features.head())

    os.makedirs(args.out, exist_ok=True)

    base = os.path.splitext(os.path.basename(args.h5_path))[0]
    out_csv = os.path.join(args.out, f"{base}_acc_magnitude_per_epoch.csv")

    epoch_features.to_csv(out_csv)
    print(f"\nSaved epoch statistics to {out_csv}")
