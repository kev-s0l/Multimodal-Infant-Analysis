import pandas as pd
import numpy as np


def print_start_time_checks(acc_df, cov_30s, sleep_df):
    print(
        sleep_df['state']
        .str.lower()
        .value_counts()
    )

    print("\n=== START TIME CHECK ===")
    print("Accel start:", acc_df.index.min())
    print("Accel end:  ", acc_df.index.max())
    print("CoV start:  ", cov_30s.index.min())
    print("CoV end:    ", cov_30s.index.max())
    print("Sleep start:", sleep_df.index.min())
    print("Sleep end:  ", sleep_df.index.max())

    offset = sleep_df.index.min() - cov_30s.index.min()
    print("Sleep start - CoV start offset:", offset)


def run_analytics(cov_30s, sleep_df, plot1_states, sleep_states, acc_df):
    print("\n========== ADVANCED CoV + SLEEP ANALYTICS ==========\n")

    print("CoV STATISTICS:")
    print(f"Mean:     {cov_30s.mean():.4f}")
    print(f"Median:   {cov_30s.median():.4f}")
    print(f"Std Dev:  {cov_30s.std():.4f}")
    print(f"Variance: {cov_30s.var():.4f}")
    print(f"Min:      {cov_30s.min():.4f}")
    print(f"Max:      {cov_30s.max():.4f}")
    print(f"P05:      {cov_30s.quantile(0.05):.4f}")
    print(f"P25:      {cov_30s.quantile(0.25):.4f}")
    print(f"P75:      {cov_30s.quantile(0.75):.4f}")
    print(f"P95:      {cov_30s.quantile(0.95):.4f}")

    sleep_only_df = sleep_df[sleep_df['state_norm'].isin(sleep_states)]
    sleep_start = sleep_only_df.index.min()
    sleep_end = sleep_only_df.index.max()
    total_sleep_seconds = (sleep_end - sleep_start).total_seconds()
    total_record_seconds = (cov_30s.index[-1] - cov_30s.index[0]).total_seconds()

    print("\nOTHER METRICS:")
    print(f"Total Sleep Window:   {total_sleep_seconds/3600:.2f} hrs")
    print(f"Total Recording Time: {total_record_seconds/3600:.2f} hrs")
    print(f"Sleep Efficiency:     {(total_sleep_seconds/total_record_seconds)*100:.1f}%")

    state_labels = sleep_df['state_norm'].reindex(
        cov_30s.index,
        method='nearest',
        tolerance=pd.Timedelta('40s')
    )
    state_cov = pd.DataFrame({
        'cov': cov_30s,
        'state': state_labels
    }).dropna(subset=['state'])

    print("\nSTATE-WISE CoV SUMMARY (30s epochs):")
    if state_cov.empty:
        print("No matched sleep-state labels within tolerance.")
    else:
        for st in plot1_states:
            st_cov = state_cov.loc[state_cov['state'] == st, 'cov']
            if st_cov.empty:
                continue
            hours = (len(st_cov) * 30) / 3600.0
            print(
                f"{st.upper():>12} | epochs: {len(st_cov):5d} | hrs: {hours:5.2f} | "
                f"mean: {st_cov.mean():.4f} | median: {st_cov.median():.4f} | "
                f"P95: {st_cov.quantile(0.95):.4f}"
            )

    hi_thr = cov_30s.quantile(0.95)
    hi_mask = cov_30s > hi_thr
    hi_blocks = (
        hi_mask.astype(int)
        .diff()
        .fillna(0)
        .ne(0)
        .cumsum()
    )
    hi_groups = cov_30s[hi_mask].groupby(hi_blocks[hi_mask])

    print("\nHIGH-CoV BURSTS (>{:.4f}):".format(hi_thr))
    if hi_mask.any():
        burst_durations = []
        burst_peaks = []
        for _, g in hi_groups:
            duration_s = len(g) * 30
            burst_durations.append(duration_s)
            burst_peaks.append(g.max())
        total_burst_s = sum(burst_durations)
        print(f"Bursts:           {len(burst_durations)}")
        print(f"Total time:       {total_burst_s/60:.1f} min")
        print(f"Mean duration:    {np.mean(burst_durations):.1f} s")
        print(f"Max duration:     {np.max(burst_durations):.1f} s")
        print(f"Peak CoV (max):   {np.max(burst_peaks):.4f}")
    else:
        print("No bursts detected above threshold.")

    print("\n=====================================================\n")

    cov_low = cov_30s.quantile(0.25)
    cov_high = cov_30s.quantile(0.75)
    activity_class = pd.cut(
        cov_30s,
        bins=[-float('inf'), cov_low, cov_high, float('inf')],
        labels=['low', 'medium', 'high']
    )
    activity_counts = activity_class.value_counts().reindex(['low', 'medium', 'high']).fillna(0).astype(int)
    activity_hours = activity_counts * 30 / 3600.0

    print("\nACTIVITY COUNTS (CoV-based):")
    for label in ['low', 'medium', 'high']:
        print(f"{label.upper():>6} | epochs: {activity_counts[label]:5d} | hrs: {activity_hours[label]:5.2f}")

    print("\nPER-STATE CoV DISTRIBUTIONS:")
    if state_cov.empty:
        print("No state-aligned data for distributions.")
    else:
        for st in plot1_states:
            st_cov = state_cov.loc[state_cov['state'] == st, 'cov']
            if st_cov.empty:
                continue
            print(
                f"{st.upper():>12} | mean: {st_cov.mean():.4f} | std: {st_cov.std():.4f} | "
                f"P25: {st_cov.quantile(0.25):.4f} | P50: {st_cov.median():.4f} | P75: {st_cov.quantile(0.75):.4f}"
            )

    print("\nTRANSITION-ALIGNED CoV (±5 min around state changes):")
    transition_window = pd.Timedelta('5min')
    transitions = sleep_df['state_norm'].ne(sleep_df['state_norm'].shift())
    transition_times = sleep_df.index[transitions]
    if len(transition_times) == 0:
        print("No transitions detected.")
    else:
        aligned_vals = []
        for t in transition_times:
            window = cov_30s.loc[
                (cov_30s.index >= t - transition_window) &
                (cov_30s.index <= t + transition_window)
            ]
            if not window.empty:
                aligned_vals.append(window.values)
        if aligned_vals:
            concat = np.concatenate(aligned_vals)
            print(
                f"Transitions: {len(transition_times)} | Samples: {len(concat)} | "
                f"Mean CoV: {np.mean(concat):.4f} | P95: {np.percentile(concat, 95):.4f}"
            )
        else:
            print("No CoV samples found in transition windows.")

    print("\nCIRCADIAN PROFILE (hourly mean CoV):")
    hourly_cov = cov_30s.groupby(cov_30s.index.hour).mean()
    for hour, val in hourly_cov.items():
        print(f"{hour:02d}:00 | mean CoV: {val:.4f}")

    print("\nSPECTRAL FEATURES (dominant frequency per 5-min window):")
    fs = 50
    win = int(fs * 300)
    mag = acc_df['mag'].values
    if len(mag) >= win:
        dom_freqs = []
        for i in range(0, len(mag) - win + 1, win):
            seg = mag[i:i+win]
            seg = seg - np.mean(seg)
            freqs = np.fft.rfftfreq(len(seg), d=1/fs)
            psd = np.abs(np.fft.rfft(seg))**2
            dom = freqs[np.argmax(psd[1:]) + 1] if len(psd) > 1 else 0
            dom_freqs.append(dom)
        print(
            f"Windows: {len(dom_freqs)} | Mean dom freq: {np.mean(dom_freqs):.2f} Hz | "
            f"P95: {np.percentile(dom_freqs,95):.2f} Hz"
        )
    else:
        print("Not enough data for 5-min spectral windows.")

    print("\nAUTOCORRELATION (first 5 min of CoV):")
    max_lag = int(5 * 60 / 30)
    if len(cov_30s) > max_lag:
        x = cov_30s.values - np.mean(cov_30s.values)
        ac = np.correlate(x, x, mode='full')[len(x)-1:len(x)+max_lag]
        ac /= ac[0] if ac[0] != 0 else 1
        peak_lag = np.argmax(ac[1:]) + 1
        print(f"Peak lag: {peak_lag*30} s | Peak corr: {ac[peak_lag]:.3f}")
    else:
        print("Not enough data for autocorrelation window.")

    return state_cov, hourly_cov