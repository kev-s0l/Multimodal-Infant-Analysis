import argparse
import os
from src.core.velocity_core import compute_velocity_stats

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute component-wise velocity stats (30s epochs)")
    parser.add_argument("h5_path", help="Path to H5 file")
    parser.add_argument("target_id", help="Sensor ID (e.g., 16162)")
    parser.add_argument("--out", default="movement_outputs", help="Output folder")
    args = parser.parse_args()

    df = compute_velocity_stats(args.h5_path, args.target_id)

    print("\n--- Component-Wise Velocity Stats (Per 30s Epoch) ---")
    print(df.head())

    os.makedirs(args.out, exist_ok=True)

    base = os.path.splitext(os.path.basename(args.h5_path))[0]
    out_csv = os.path.join(args.out, f"{base}_velocity_stats.csv")

    df.to_csv(out_csv)
    print(f"\nSaved velocity statistics to {out_csv}")
