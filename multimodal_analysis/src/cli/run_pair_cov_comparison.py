import argparse
from pathlib import Path
import pandas as pd

from core.pair_cov_loader import load_sleep_df, load_acc_df
from core.pair_cov_processing import prepare_acc_df, cov_30s_from_acc
from core.pair_cov_summary import summarize_subject, pairwise_comparison


def main():
    parser = argparse.ArgumentParser(
        description="Compare CoV summary stats across subject pairs."
    )

    parser.add_argument(
        "--manifest",
        required=True,
        help="CSV with pair_id,subject_label,h5_path,sleep_path,target_id."
    )

    parser.add_argument(
        "--out-dir",
        default="reports",
        help="Output directory for CSV reports."
    )

    args = parser.parse_args()

    manifest = pd.read_csv(args.manifest)

    required_cols = {
        "pair_id",
        "subject_label",
        "h5_path",
        "sleep_path",
        "target_id"
    }
    missing = required_cols - set(manifest.columns)
    if missing:
        raise ValueError(f"Manifest missing columns: {sorted(missing)}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []

    for _, row in manifest.iterrows():
        pair_id = row["pair_id"]
        subject_label = row["subject_label"]
        h5_path = row["h5_path"]
        sleep_path = row["sleep_path"]
        target_id = row["target_id"]

        sleep_df, _ = load_sleep_df(sleep_path)
        acc_df = load_acc_df(h5_path, target_id)
        acc_df = prepare_acc_df(acc_df)
        cov_30s = cov_30s_from_acc(acc_df)
        stats = summarize_subject(cov_30s, sleep_df)

        rows.append(
            {
                "pair_id": pair_id,
                "subject_label": subject_label,
                "h5_path": h5_path,
                "sleep_path": sleep_path,
                "target_id": target_id,
                **stats,
            }
        )

    summary_df = pd.DataFrame(rows)
    summary_path = out_dir / "subject_summary.csv"
    summary_df.to_csv(summary_path, index=False)

    compare_df = pairwise_comparison(
        summary_df,
        id_cols=["pair_id", "subject_label", "h5_path", "sleep_path", "target_id"]
    )
    compare_path = out_dir / "pair_comparison.csv"
    compare_df.to_csv(compare_path, index=False)

    print(f"Wrote: {summary_path}")
    print(f"Wrote: {compare_path}")


if __name__ == "__main__":
    main()