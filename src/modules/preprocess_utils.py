
import datetime
import math
import re

import numpy as np
import pandas as pd

import config
import consts


def round_timestamp(df):
    df[consts.TIMESTAMP_COLUMN_NAME] = df[consts.TIMESTAMP_COLUMN_NAME].apply(round_datetime)
    return df


def round_datetime(date_time):
    year = date_time.year
    month = date_time.month
    day = date_time.day
    hour = date_time.hour
    minute = date_time.minute
    second = 0
    millisecond = 0

    if minute % 3 != 0:
        if (minute - 1) % 3 == 0:
            minute -= 1
        elif (minute + 1) % 3 == 0:
            minute += 1
        minute = minute % 60

    date_time = datetime.datetime(year, month, day, hour, minute, second, millisecond)
    return date_time


def interpolate_t(df, min_datetime, max_datetime, t_column_name=consts.BOILER_T_COLUMN_NAME):
    df = interpolate_first_t(df, min_datetime, t_column_name)
    df = interpolate_last_t(df, max_datetime, t_column_name)
    df = interpolate_passes_of_t(df, t_column_name)
    return df


def interpolate_passes_of_t(df, t_column_name=consts.BOILER_T_COLUMN_NAME):
    df.sort_values(by=consts.TIMESTAMP_COLUMN_NAME, ignore_index=True, inplace=True)

    interpolated_values = []

    previous_datetime = None
    previous_t = None
    for index, row in df.iterrows():

        if previous_datetime is None:
            previous_datetime = row[consts.TIMESTAMP_COLUMN_NAME]
            previous_t = row[t_column_name]
            continue

        next_datetime = row[consts.TIMESTAMP_COLUMN_NAME]
        next_t = row[t_column_name]

        datetime_delta = next_datetime - previous_datetime
        if datetime_delta > config.TIME_STEP:
            number_of_passes = int(datetime_delta.total_seconds() // config.TIME_STEP.seconds) - 1
            t_step = (next_t - previous_t) / number_of_passes
            for pass_n in range(1, number_of_passes + 1):
                interpolated_datetime = previous_datetime + (config.TIME_STEP * pass_n)
                interpolated_t = previous_t + (t_step * pass_n)
                interpolated_values.append({
                    consts.TIMESTAMP_COLUMN_NAME: interpolated_datetime,
                    t_column_name: interpolated_t,
                })

        previous_t = next_t
        previous_datetime = next_datetime

    df = df.append(interpolated_values)
    df.sort_values(by=consts.TIMESTAMP_COLUMN_NAME, ignore_index=True, inplace=True)

    return df


def interpolate_first_t(df, min_datetime, t_column_name=consts.BOILER_T_COLUMN_NAME):
    min_datetime = round_datetime(min_datetime)

    first_datetime_idx = df[consts.TIMESTAMP_COLUMN_NAME].idxmin()
    first_row = df.loc[first_datetime_idx]
    first_t = first_row[t_column_name]
    first_datetime = first_row[consts.TIMESTAMP_COLUMN_NAME]
    if first_datetime > min_datetime:
        df = df.append(
            {consts.TIMESTAMP_COLUMN_NAME: min_datetime, t_column_name: first_t},
            ignore_index=True
        )
    return df


def interpolate_last_t(df, max_datetime, t_column_name=consts.BOILER_T_COLUMN_NAME):
    max_datetime = round_datetime(max_datetime)

    last_datetime_idx = df[consts.TIMESTAMP_COLUMN_NAME].idxmax()
    last_row = df.loc[last_datetime_idx]
    last_t = last_row[t_column_name]
    last_datetime = last_row[consts.TIMESTAMP_COLUMN_NAME]
    if last_datetime < max_datetime:
        df = df.append(
            {consts.TIMESTAMP_COLUMN_NAME: max_datetime, t_column_name: last_t},
            ignore_index=True
        )
    return df


def filter_by_timestamp(df, min_date, max_date):
    df = df[
        (df[consts.TIMESTAMP_COLUMN_NAME] >= min_date) &
        (df[consts.TIMESTAMP_COLUMN_NAME] <= max_date)
        ]
    return df


# noinspection SpellCheckingInspection
def average_values(x, window_len=4, window='hanning'):
    if x.ndim != 1:
        raise ValueError("smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.")

    if window not in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")

    if window_len < 3:
        return x

    s = np.r_[x[window_len - 1:0:-1], x, x[-2:-window_len - 1:-1]]

    if window == 'flat':
        w = np.ones(window_len, 'd')
    else:
        w = getattr(np, window)(window_len)

    y = np.convolve(w / w.sum(), s, mode='valid')
    return y[(window_len // 2 - 1 + (window_len % 2)):-(window_len // 2)]
    # return y


def remove_duplicates_by_timestamp(df):
    df.drop_duplicates(consts.TIMESTAMP_COLUMN_NAME, inplace=True, ignore_index=True)
    return df


def reset_index(df):
    df.reset_index(drop=True, inplace=True)
    return df


def exclude_rows_without_value(df, column_name=consts.BOILER_T_COLUMN_NAME):
    df = df[df[column_name].notnull()]
    return df


def convert_to_float(df, column_name=consts.BOILER_T_COLUMN_NAME):
    df[column_name] = df[column_name].apply(float_converter)
    return df


def float_converter(value):
    if isinstance(value, str):
        value = value.replace(",", ".")
    value = float(value)
    return value


def remove_t_bad_zeros(df, column_name=consts.BOILER_T_COLUMN_NAME):
    df[column_name] = df[column_name].apply(lambda t: t > 100 and t / 100 or t)
    return df


def remove_disabled_t(df, disabled_t_threshold, column_name=consts.BOILER_T_COLUMN_NAME):
    if disabled_t_threshold:
        df = df[df[column_name] > disabled_t_threshold]
    return df


def convert_date_and_time_to_timestamp(df):
    timestamps = []
    for index, row in df.iterrows():
        parsed = re.match(r"(?P<hour>\d\d):(?P<min>\d\d):(?P<sec>\d\d)", row[consts.SOFT_M_TIME_COLUMN_NAME])
        h, m, s = int(parsed.group("hour")), int(parsed.group("min")), int(parsed.group("sec"))
        time = pd.Timedelta(hours=h, minutes=m, seconds=s)
        timestamp = row[consts.SOFT_M_DATE_COLUMN_NAME] + time
        timestamps.append(timestamp)

    df[consts.TIMESTAMP_COLUMN_NAME] = timestamps
    del df[consts.SOFT_M_DATE_COLUMN_NAME]
    del df[consts.SOFT_M_TIME_COLUMN_NAME]

    return df


def rename_column(df, src_name, dst_name):
    df[dst_name] = df[src_name]
    del df[src_name]
    return df


def round_down(df, column_name=consts.BOILER_T_COLUMN_NAME):
    df[column_name] = df[column_name].apply(math.floor)
    return df


def convert_str_to_timestamp(df):
    df[consts.TIMESTAMP_COLUMN_NAME] = df[consts.TIMESTAMP_COLUMN_NAME].apply(parse_timestamp)
    return df


def parse_timestamp(time_str):
    parsed = re.match(
        r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})\s(?P<hour>\d{2}):(?P<min>\d{2}).{7}",
        time_str
    )
    if parsed is None:
        parsed = re.match(
            r"(?P<day>\d{2})\.(?P<month>\d{2})\.(?P<year>\d{4})\s(?P<hour>\d{1,2}):(?P<min>\d{2})",
            time_str
        )

    year = int(parsed.group("year"))
    month = int(parsed.group("month"))
    day = int(parsed.group("day"))
    hour = int(parsed.group("hour"))
    minute = int(parsed.group("min"))
    second = 0
    millisecond = 0

    date_time = datetime.datetime(year, month, day, hour, minute, second, millisecond)
    return date_time


def get_min_max_datetime(df):
    if df.empty:
        return None, None

    min_date = df[consts.TIMESTAMP_COLUMN_NAME].min()
    max_date = df[consts.TIMESTAMP_COLUMN_NAME].max()
    return min_date, max_date
