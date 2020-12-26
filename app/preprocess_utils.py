import datetime
import math
import re

import data_consts


def round_timestamp(df):
    df[data_consts.TIMESTAMP_COLUMN_NAME] = df[data_consts.TIMESTAMP_COLUMN_NAME].apply(round_datetime)
    return df


def round_datetime(src_datetime):
    src_timestamp = src_datetime.timestamp()
    time_step_in_seconds = data_consts.TIME_TICK.total_seconds()
    rounded_timestamp = math.ceil(src_timestamp / time_step_in_seconds) * time_step_in_seconds
    rounded_datetime = datetime.datetime.fromtimestamp(rounded_timestamp, tz=src_datetime.tzinfo)
    return rounded_datetime


def interpolate_t(df, min_datetime=None, max_datetime=None, t_column_name=data_consts.BOILER_PIPE_1_COLUMN_NAME):
    if min_datetime is not None:
        df = interpolate_first_t(df, min_datetime, t_column_name)
    if max_datetime is not None:
        df = interpolate_last_t(df, max_datetime, t_column_name)
    df = interpolate_passes_of_t(df, t_column_name)
    return df


def interpolate_first_t(df, min_datetime, t_column_name=data_consts.BOILER_PIPE_1_COLUMN_NAME):
    min_datetime = round_datetime(min_datetime)

    first_datetime_idx = df[data_consts.TIMESTAMP_COLUMN_NAME].idxmin()
    first_row = df.loc[first_datetime_idx]
    first_t = first_row[t_column_name]
    first_datetime = first_row[data_consts.TIMESTAMP_COLUMN_NAME]
    if first_datetime > min_datetime:
        df = df.append(
            {data_consts.TIMESTAMP_COLUMN_NAME: min_datetime, t_column_name: first_t},
            ignore_index=True
        )
    return df


def interpolate_last_t(df, max_datetime, t_column_name=data_consts.BOILER_PIPE_1_COLUMN_NAME):
    max_datetime = round_datetime(max_datetime)

    last_datetime_idx = df[data_consts.TIMESTAMP_COLUMN_NAME].idxmax()
    last_row = df.loc[last_datetime_idx]
    last_t = last_row[t_column_name]
    last_datetime = last_row[data_consts.TIMESTAMP_COLUMN_NAME]
    if last_datetime < max_datetime:
        df = df.append(
            {data_consts.TIMESTAMP_COLUMN_NAME: max_datetime, t_column_name: last_t},
            ignore_index=True
        )
    return df


def interpolate_passes_of_t(df, t_column_name=data_consts.BOILER_PIPE_1_COLUMN_NAME):
    df = sort_by_timestamp(df)

    interpolated_values = []

    previous_datetime = None
    previous_t = None
    for index, row in df.iterrows():

        if previous_datetime is None:
            previous_datetime = row[data_consts.TIMESTAMP_COLUMN_NAME]
            previous_t = row[t_column_name]
            continue

        next_datetime = row[data_consts.TIMESTAMP_COLUMN_NAME]
        next_t = row[t_column_name]

        datetime_delta = next_datetime - previous_datetime
        if datetime_delta > data_consts.TIME_TICK:
            number_of_passes = int(datetime_delta // data_consts.TIME_TICK) - 1
            t_step = (next_t - previous_t) / number_of_passes
            for pass_n in range(1, number_of_passes + 1):
                interpolated_datetime = previous_datetime + (data_consts.TIME_TICK * pass_n)
                interpolated_t = previous_t + (t_step * pass_n)
                interpolated_values.append({
                    data_consts.TIMESTAMP_COLUMN_NAME: interpolated_datetime,
                    t_column_name: interpolated_t,
                })

        previous_t = next_t
        previous_datetime = next_datetime

    df = df.append(interpolated_values)
    df = sort_by_timestamp(df)

    return df


def sort_by_timestamp(df):
    df.sort_values(by=data_consts.TIMESTAMP_COLUMN_NAME, ignore_index=True, inplace=True)
    return df


def filter_by_timestamp(df, min_date, max_date):
    df = df[
        (df[data_consts.TIMESTAMP_COLUMN_NAME] >= min_date) &
        (df[data_consts.TIMESTAMP_COLUMN_NAME] < max_date)
        ]
    return df


def remove_duplicates_by_timestamp(df):
    df.drop_duplicates(data_consts.TIMESTAMP_COLUMN_NAME, inplace=True, ignore_index=True)
    return df


# noinspection SpellCheckingInspection
def convert_date_and_time_to_timestamp(df, tzinfo=None):
    datetime_list = []
    for _, row in df.iterrows():
        time_as_str = row[data_consts.SOFT_M_TIME_COLUMN_NAME]
        time = parse_time(time_as_str)

        date = row[data_consts.SOFT_M_DATE_COLUMN_NAME].date()

        datetime_ = datetime.datetime.combine(date, time, tzinfo=tzinfo)
        datetime_list.append(datetime_)

    df[data_consts.TIMESTAMP_COLUMN_NAME] = datetime_list
    del df[data_consts.SOFT_M_DATE_COLUMN_NAME]
    del df[data_consts.SOFT_M_TIME_COLUMN_NAME]

    return df


def parse_time(time_as_str):
    parsed = re.match(r"(?P<hour>\d\d):(?P<min>\d\d):(?P<sec>\d\d)", time_as_str)
    hour = int(parsed.group("hour"))
    minute = int(parsed.group("min"))
    second = int(parsed.group("sec"))
    time = datetime.time(hour=hour, minute=minute, second=second)
    return time


def rename_column(df, src_name, dst_name):
    df[dst_name] = df[src_name]
    del df[src_name]
    return df


def parse_datetime(datetime_as_str, datetime_patterns=data_consts.DATETIME_PATTERNS, timezone=None):
    for pattern in datetime_patterns:
        parsed = re.match(pattern, datetime_as_str)
        if parsed is not None:
            break
    else:
        raise ValueError("Date and time are not matched using existing patterns")

    year = int(parsed.group("year"))
    month = int(parsed.group("month"))
    day = int(parsed.group("day"))
    hour = int(parsed.group("hours"))
    minute = int(parsed.group("minutes"))
    second = 0
    millisecond = 0

    datetime_ = datetime.datetime(year, month, day, hour, minute, second, millisecond, tzinfo=timezone)
    return datetime_


def get_min_max_timestamp(df):
    if df.empty:
        return None, None

    min_date = df[data_consts.TIMESTAMP_COLUMN_NAME].min()
    max_date = df[data_consts.TIMESTAMP_COLUMN_NAME].max()
    return min_date, max_date
