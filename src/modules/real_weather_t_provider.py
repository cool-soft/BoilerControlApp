import json
import threading

import config
from modules.preprocess_utils import (
    round_datetime,
    interpolate_t,
    remove_duplicates_by_timestamp,
    round_timestamp,
    convert_date_and_time_to_timestamp,
    filter_by_timestamp,

)

import pandas as pd
import requests


class RealWeatherTProvider:

    def __init__(self):
        self._cache_size = config.PROVIDER_VALUES_CACHE_SIZE
        self._real_weather_t_cache = pd.DataFrame()
        self._cache_access_lock = threading.RLock()

    def get_real_weather_t(self, min_date, max_date):
        min_date = round_datetime(min_date)
        max_date = round_datetime(max_date)

        with self._cache_access_lock:
            dates_for_request = self._get_need_min_max_dates_with_cache(min_date, max_date)
            if dates_for_request is not None:
                min_request_date, max_request_date = dates_for_request
                df = self._request_from_server(min_request_date, max_request_date)
                df = self._preprocess_weather_t(df, min_request_date, max_request_date)
                self._update_cache(df)

            return self._get_from_cache(min_date, max_date)

    def _get_need_min_max_dates_with_cache(self, min_date, max_date):
        cached_dates = self._get_min_max_cached_dates()
        if cached_dates is None:
            return min_date, max_date
        min_cached_date, max_cached_date = cached_dates

        if min_date < min_cached_date <= max_date:
            return min_date, min_cached_date

        if min_cached_date <= min_date and max_cached_date <= max_date:
            return None, None

        if min_date >= min_cached_date and max_cached_date < max_date:
            return max_cached_date, max_date

        return min_date, max_date

    def _get_min_max_cached_dates(self):
        if self._real_weather_t_cache.empty:
            return None

        first_date_idx = self._real_weather_t_cache[config.TIMESTAMP_COLUMN_NAME].idxmin()
        first_row = self._real_weather_t_cache.loc[first_date_idx]
        min_cached_date = first_row[config.TIMESTAMP_COLUMN_NAME]

        last_date_idx = self._real_weather_t_cache[config.TIMESTAMP_COLUMN_NAME].idxmax()
        last_row = self._real_weather_t_cache.loc[last_date_idx]
        max_cached_date = last_row[config.TIMESTAMP_COLUMN_NAME]

        return min_cached_date, max_cached_date

    # noinspection PyMethodMayBeStatic
    def _request_from_server(self, min_request_date, max_request_date):
        url = f"{config.REMOTE_HOST}/JSON/"
        params = {
            "method": "getWeatherM",
            "argument": json.dumps({
                "db": min_request_date.isoformat(sep=" ", timespec="seconds"),
                "de": max_request_date.isoformat(sep=" ", timespec="seconds")
            })
        }
        response = requests.get(url, params=params)
        df = pd.read_json(response.text)

        return df

    # noinspection PyMethodMayBeStatic
    def _preprocess_weather_t(self, df, min_date, max_date):
        df = convert_date_and_time_to_timestamp(df)
        df = round_timestamp(df)
        df = interpolate_t(df, min_date, max_date, t_column_name="temp")
        df = remove_duplicates_by_timestamp(df)
        return df

    def _update_cache(self, df):
        self._real_weather_t_cache = self._real_weather_t_cache.append(df)
        self._real_weather_t_cache = remove_duplicates_by_timestamp(df)

    def _get_from_cache(self, min_date, max_date):
        return filter_by_timestamp(self._real_weather_t_cache, min_date, max_date).copy()

    def compact_cache(self):
        with self._cache_access_lock:
            pass
        # TODO: this
