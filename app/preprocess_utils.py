import datetime
import math
import re


def round_datetime(src_datetime, time_tick_in_seconds):
    src_timestamp = src_datetime.timestamp()
    time_step_in_seconds = time_tick_in_seconds
    rounded_timestamp = math.ceil(src_timestamp / time_step_in_seconds) * time_step_in_seconds
    rounded_datetime = datetime.datetime.fromtimestamp(rounded_timestamp, tz=src_datetime.tzinfo)
    return rounded_datetime


def parse_datetime(datetime_as_str, datetime_patterns, timezone=None):
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


def parse_time(time_as_str, time_parse_pattern):
    parsed = re.match(time_parse_pattern, time_as_str)
    hour = int(parsed.group("hour"))
    minute = int(parsed.group("min"))
    second = int(parsed.group("sec"))
    time = datetime.time(hour=hour, minute=minute, second=second)
    return time
