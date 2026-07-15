import numpy as np
from scipy.signal import butter, filtfilt


def butter_lowpass_filter(data, cutoff=3, fs=50, order=4):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype="low")
    return filtfilt(b, a, data)


def prepare_acc_df(acc_df):
    acc_df = acc_df.copy()

    acc_df["mag"] = np.sqrt(
        acc_df["ax"] ** 2 + acc_df["ay"] ** 2 + acc_df["az"] ** 2
    )

    acc_df["mag"] = acc_df["mag"].clip(
        lower=acc_df["mag"].quantile(0.01),
        upper=acc_df["mag"].quantile(0.99),
    )

    acc_df["mag"] -= acc_df["mag"].rolling(
        window=250,
        center=True,
        min_periods=1
    ).mean()

    acc_df["mag"] = butter_lowpass_filter(
        acc_df["mag"].interpolate(),
        cutoff=3,
        fs=50
    )

    acc_df.dropna(inplace=True)
    return acc_df


def cov_30s_from_acc(acc_df):
    def cov_func(x):
        mean_x = x.mean()
        return np.nan if mean_x == 0 else x.std() / mean_x

    return acc_df["mag"].resample("30s").apply(cov_func).dropna()