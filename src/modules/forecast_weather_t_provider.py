
import threading


import config
from modules.preprocess_utils import (
    interpolate_t,
    remove_duplicates_by_timestamp,
    round_timestamp,
    convert_date_and_time_to_timestamp,
    filter_by_timestamp,
    get_min_max_dates_from_dataframe,

)

import pandas as pd
import requests


class ForecastWeatherTProvider:

    def __init__(self):
        self._forecast_weather_t_cache = pd.DataFrame()
        self._cache_access_lock = threading.RLock()

    def get_forecast_weather_t(self, min_date, max_date):
        with self._cache_access_lock:
            if self._is_need_request_server(max_date):
                df = self._request_from_server()
                df = self._preprocess_weather_t(df)
                self._update_cache(df)

            return self._get_from_cache(min_date, max_date)

    def _is_need_request_server(self, max_date):
        max_cached_date = self._get_max_cached_date()

        if max_cached_date is None:
            return True

        if max_cached_date < max_date:
            return True

        return False

    def _get_max_cached_date(self):
        min_cached_date, max_cached_date = get_min_max_dates_from_dataframe(self._forecast_weather_t_cache)
        return max_cached_date

    # noinspection PyMethodMayBeStatic
    def _request_from_server(self):
        url = f"{config.REMOTE_HOST}/JSON/"
        # noinspection SpellCheckingInspection
        params = {
            "method": "getPrognozT"
        }
        response = requests.get(url, params=params)
        df = pd.read_json(response.text)

        return df

    # noinspection PyMethodMayBeStatic
    def _preprocess_weather_t(self, df):
        df = convert_date_and_time_to_timestamp(df)
        df = round_timestamp(df)
        min_date, max_date = get_min_max_dates_from_dataframe(df)
        df = interpolate_t(df, min_date, max_date, t_column_name="temp")
        df = remove_duplicates_by_timestamp(df)
        return df

    def _update_cache(self, df):
        self._forecast_weather_t_cache = pd.concat(
            [self._forecast_weather_t_cache, df], ignore_index=True
        )
        self._forecast_weather_t_cache = remove_duplicates_by_timestamp(self._forecast_weather_t_cache)

    def _get_from_cache(self, min_date, max_date):
        return filter_by_timestamp(self._forecast_weather_t_cache, min_date, max_date).copy()

    def compact_cache(self):
        with self._cache_access_lock:
            pass
        # TODO: this
