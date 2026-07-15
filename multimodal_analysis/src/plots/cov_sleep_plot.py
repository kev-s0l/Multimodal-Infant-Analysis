import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch
from matplotlib.lines import Line2D


def plot_continuous_cov(cov_30s, sleep_df, plot1_states, plot1_colors, title):
    plot1_df = sleep_df[sleep_df['state_norm'].isin(plot1_states)]

    fig, ax = plt.subplots(figsize=(15, 7))

    ax.plot(
        cov_30s.index, cov_30s.values,
        color='magenta', lw=1.5,
        solid_capstyle="butt", solid_joinstyle="round"
    )

    epoch = cov_30s.index.to_series().diff().median()
    if pd.isna(epoch) or epoch <= pd.Timedelta(0):
        epoch = pd.Timedelta(seconds=30)

    half = epoch / 2

    for state, color in plot1_colors.items():
        state_df = plot1_df[plot1_df['state_norm'] == state].copy()
        state_df['gap'] = (
            state_df.index.to_series().diff() > pd.Timedelta('40s')
        ).cumsum()

        for _, blk in state_df.groupby('gap'):
            left = blk.index.min() - half
            right = blk.index.max() + half

            ax.axvspan(
                left,
                right,
                color=color,
                alpha=0.25,
                linewidth=0
            )

    ax.margins(x=0)

    legend1 = (
        [Patch(facecolor=color, edgecolor="none", alpha=0.25, label=state.upper())
         for state, color in plot1_colors.items()] +
        [Line2D([0], [0], color='magenta', lw=1.5, label='CoV')]
    )
    ax.legend(handles=legend1, loc='upper right')

    ax.set_title(title)
    ax.set_xlabel("Time")
    ax.set_ylabel("Coefficient of Variation")
    ax.grid(True)

    overlap_start = max(cov_30s.index.min(), plot1_df.index.min())
    overlap_end = min(cov_30s.index.max(), plot1_df.index.max())
    ax.set_xlim(overlap_start, overlap_end)
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=6, maxticks=10))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

    plt.tight_layout()
    plt.show()


def plot_compressed_sleep_cov(
    cov_30s,
    sleep_df,
    sleep_start_dt,
    sleep_states,
    sleep_colors,
    title
):
    fig2, ax2 = plt.subplots(figsize=(15, 7))

    sleep_only_df = sleep_df[sleep_df['state_norm'].isin(sleep_states)]

    sleep_labels = sleep_only_df['state'].reindex(
        cov_30s.index,
        method='nearest',
        tolerance=pd.Timedelta('40s')
    )

    sleep_mask = sleep_labels.str.lower().isin(sleep_states)
    sleep_cov = cov_30s[sleep_mask].copy()
    sleep_state_for_cov = sleep_labels[sleep_mask].str.lower()

    df_blocks = pd.DataFrame({
        'state': sleep_state_for_cov,
        'original_time': sleep_cov.index
    })

    df_blocks['time_diff'] = df_blocks['original_time'].diff()
    df_blocks['block_id'] = (
        (df_blocks['state'] != df_blocks['state'].shift()) |
        (df_blocks['time_diff'] > pd.Timedelta('40s'))
    ).cumsum()

    time_mapping = {}
    current_time = pd.Timedelta(0)

    for block_id in sorted(df_blocks['block_id'].unique()):
        group = df_blocks[df_blocks['block_id'] == block_id]
        block_start = group['original_time'].min()
        block_duration = (
            group['original_time'].max() - block_start +
            pd.Timedelta('30s')
        )

        for t in group['original_time']:
            time_mapping[t] = current_time + (t - block_start)

        current_time += block_duration

    compressed_times = [time_mapping[t] for t in sleep_cov.index]
    sleep_cov_compressed = sleep_cov.copy()
    sleep_cov_compressed.index = (
        pd.to_datetime(sleep_start_dt) +
        pd.to_timedelta(compressed_times)
    )

    ax2.plot(
        sleep_cov_compressed.index,
        sleep_cov_compressed.values,
        color='magenta',
        lw=1.5
    )

    for state in sleep_states:
        mask = sleep_state_for_cov == state
        if not mask.any():
            continue

        idx = sleep_cov_compressed.index[mask]
        ax2.axvspan(
            idx.min(),
            idx.max(),
            color=sleep_colors[state],
            alpha=0.25
        )

    legend2 = (
        [Patch(facecolor=color, alpha=0.25, label=state.upper())
         for state, color in sleep_colors.items()] +
        [Patch(facecolor='magenta', alpha=0.5, label='CoV')]
    )

    ax2.legend(handles=legend2, loc='upper right')
    ax2.set_title(title)
    ax2.set_xlabel("Compressed Sleep Time")
    ax2.set_ylabel("Coefficient of Variation")
    ax2.grid(True)

    ax2.set_xlim(
        sleep_cov_compressed.index.min(),
        sleep_cov_compressed.index.max()
    )
    ax2.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=6, maxticks=10))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

    plt.tight_layout()
    plt.show()


def plot_cov_distribution_by_state(state_cov, plot1_states):
    fig3, ax3 = plt.subplots(figsize=(10, 5))

    data = [
        state_cov.loc[state_cov['state'] == st, 'cov']
        for st in plot1_states
        if not state_cov.loc[state_cov['state'] == st, 'cov'].empty
    ]
    labels = [
        st.upper()
        for st in plot1_states
        if not state_cov.loc[state_cov['state'] == st, 'cov'].empty
    ]

    if data:
        ax3.boxplot(data, tick_labels=labels, showfliers=False)
        ax3.set_title('CoV Distribution by Sleep State')
        ax3.set_ylabel('Coefficient of Variation')
        ax3.grid(True, axis='y')
        plt.tight_layout()
        plt.show()


def plot_hourly_cov(hourly_cov):
    fig4, ax4 = plt.subplots(figsize=(10, 4))
    ax4.plot(hourly_cov.index, hourly_cov.values, marker='o')
    ax4.set_title('Hourly Mean CoV (Circadian Profile)')
    ax4.set_xlabel('Hour of Day')
    ax4.set_ylabel('Mean CoV')
    ax4.grid(True)
    plt.tight_layout()
    plt.show()