
import datetime
import math
import re

import numpy as np
import pandas as pd

from config import TIME_STEP, TIMESTAMP_COLUMN_NAME


def round_timestamp(df):
    df[TIMESTAMP_COLUMN_NAME] = df[TIMESTAMP_COLUMN_NAME].apply(round_datetime)
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


def interpolate_t(df, min_date, max_date, t_column_name="t1"):
    min_date = round_datetime(min_date)
    max_date = round_datetime(max_date)

    first_date_idx = df[TIMESTAMP_COLUMN_NAME].idxmin()
    first_row = df.loc[first_date_idx]
    first_t = first_row[t_column_name]
    first_date = first_row[TIMESTAMP_COLUMN_NAME]
    if first_date > min_date:
        df = df.append(
            {TIMESTAMP_COLUMN_NAME: min_date, t_column_name: first_t},
            ignore_index=True
        )

    last_date_idx = df[TIMESTAMP_COLUMN_NAME].idxmax()
    last_row = df.loc[last_date_idx]
    last_t = last_row[t_column_name]
    last_date = last_row[TIMESTAMP_COLUMN_NAME]
    if last_date < max_date:
        df = df.append(
            {TIMESTAMP_COLUMN_NAME: max_date, t_column_name: last_t},
            ignore_index=True
        )

    df.sort_values(by=TIMESTAMP_COLUMN_NAME, ignore_index=True, inplace=True)

    previous_date = None
    previous_t = None
    interpolated_values = []
    for index, row in df.iterrows():

        if previous_date is None:
            previous_date = row[TIMESTAMP_COLUMN_NAME]
            previous_t = row[t_column_name]
            continue

        next_date = row[TIMESTAMP_COLUMN_NAME]
        next_t = row[t_column_name]

        if (next_date - previous_date) > TIME_STEP:
            dates_delta = next_date - previous_date
            number_of_passes = int(dates_delta.total_seconds() // TIME_STEP.seconds) - 1
            t_step = (next_t - previous_t) / number_of_passes
            for pass_n in range(1, number_of_passes + 1):
                new_date = previous_date + (TIME_STEP * pass_n)
                new_t = previous_t + (t_step * pass_n)
                interpolated_values.append({
                    TIMESTAMP_COLUMN_NAME: new_date,
                    t_column_name: new_t,
                })

                # print(f"Interpolated: "
                #       f"{new_date}, {round(new_t, 2)}, "
                #       f"({previous_date}, {previous_t} - {next_date}, {next_t})")

        previous_t = next_t
        previous_date = next_date

    df = df.append(interpolated_values)
    df.sort_values(by=TIMESTAMP_COLUMN_NAME, ignore_index=True, inplace=True)

    return df


def filter_by_timestamp(df, min_date, max_date):
    df = df[(df[TIMESTAMP_COLUMN_NAME] >= min_date) & (df[TIMESTAMP_COLUMN_NAME] <= max_date)]
    return df


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
    df.drop_duplicates(TIMESTAMP_COLUMN_NAME, inplace=True, ignore_index=True)
    return df


def reset_index(df):
    df.reset_index(drop=True, inplace=True)
    return df


def exclude_rows_without_value(df, column_name="t1"):
    df = df[df[column_name].notnull()]
    return df


def convert_to_float(df, column_name="t1"):
    df[column_name] = df[column_name].apply(float_converter)
    return df


def float_converter(value):
    if not isinstance(value, (str, float)):
        print("!!!", type(value))

    if isinstance(value, str):
        value = value.replace(",", ".")
    value = float(value)
    return value


def remove_t_bad_zeros(df, column_name="t1"):
    df[column_name] = df[column_name].apply(lambda t: t > 100 and t / 100 or t)
    return df


def remove_disabled_t(df, disabled_t_threshold, column_name="t1"):
    if disabled_t_threshold:
        df = df[df[column_name] > disabled_t_threshold]
    return df


def convert_date_and_time_to_timestamp(df):
    timestamps = []
    for index, row in df.iterrows():
        parsed = re.match(r"(?P<h>\d\d):(?P<m>\d\d):(?P<s>\d\d)", row["time"])
        h, m, s = int(parsed.group("h")), int(parsed.group("m")), int(parsed.group("s"))
        time = pd.Timedelta(hours=h, minutes=m, seconds=s)
        timestamp = row["date"] + time
        timestamps.append(timestamp)

    df[TIMESTAMP_COLUMN_NAME] = timestamps
    del df["date"]
    del df["time"]

    return df


def rename_column(df, src_name, dst_name):
    df[dst_name] = df[src_name]
    del df[src_name]
    return df


def round_down(df, column_name="t1"):
    df[column_name] = df[column_name].apply(math.floor)
    return df


def convert_str_to_timestamp(df):
    df[TIMESTAMP_COLUMN_NAME] = df[TIMESTAMP_COLUMN_NAME].apply(parse_timestamp)
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


def prepare_data(data, min_date, max_date, disabled_t_threshold, t_column_name="t1", ntc=1):
    df = data[data["nTC"] == ntc].copy()
    df = df[[t_column_name, TIMESTAMP_COLUMN_NAME]]
    df = exclude_rows_without_value(df, t_column_name)
    df = convert_str_to_timestamp(df)
    df = filter_by_timestamp(df, min_date, max_date)
    df = convert_to_float(df, t_column_name)
    df = round_timestamp(df)
    df = remove_t_bad_zeros(df, t_column_name)
    df = remove_disabled_t(df, disabled_t_threshold, t_column_name)
    df = interpolate_t(df, min_date, max_date, t_column_name=t_column_name)
    df = remove_duplicates_by_timestamp(df)
    return df
