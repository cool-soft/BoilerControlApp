from datetime import datetime

import pandas as pd
import requests
from dateutil.tz import tzlocal

import consts
from dataset_utils.preprocess_utils import (
    rename_column,
    remove_duplicates_by_timestamp,
    convert_date_and_time_to_timestamp,
    filter_by_timestamp,
    get_min_max_timestamp,
    round_timestamp,
    interpolate_passes_of_t
)


class WeatherForecastProvider:

    def __init__(self):
        self._cached_weather_forecast_df = pd.DataFrame()
        self._forecast_weather_server_timezone = None
        self._forecast_weather_server_address = None
        self._weather_forecast_update_interval = 1800
        self._cached_weather_forecast_last_update = None

    def set_weather_forecast_server_timezone(self, server_timezone):
        self._forecast_weather_server_timezone = server_timezone

    def set_weather_forecast_server_address(self, server_address):
        self._forecast_weather_server_address = server_address

    def set_weather_forecast_update_interval(self, lifetime):
        self._weather_forecast_update_interval = lifetime

    def get_weather_forecast(self, min_date, max_date):
        if self._is_requested_datetime_not_in_cache(max_date) or \
                self._is_cached_weather_forecast_expired():
            self._update_cache_from_server()

        return self._get_from_cache(min_date, max_date)

    def _is_requested_datetime_not_in_cache(self, requested_datetime):
        _, max_cached_datetime = get_min_max_timestamp(self._cached_weather_forecast_df)
        if max_cached_datetime is None:
            return True
        if max_cached_datetime <= requested_datetime:
            return True
        return False

    def _is_cached_weather_forecast_expired(self):
        if self._cached_weather_forecast_last_update is None:
            return True

        datetime_now = datetime.now(tzlocal())
        weather_forecast_lifetime = (datetime_now - self._cached_weather_forecast_last_update)
        if weather_forecast_lifetime.total_seconds() > self._weather_forecast_update_interval:
            return True

        return False

    def _update_cache_from_server(self):
        data = self._get_weather_forecast_from_server()
        new_weather_forecast_df = self._preprocess_weather_forecast(data)
        self._cached_weather_forecast_df = new_weather_forecast_df
        self._cached_weather_forecast_last_update = datetime.now(tzlocal())

    # noinspection PyMethodMayBeStatic
    def _get_weather_forecast_from_server(self):
        url = f"{self._forecast_weather_server_address}/JSON/"
        # noinspection SpellCheckingInspection
        params = {
            "method": "getPrognozT"
        }
        response = requests.get(url, params=params)
        return response.text

    # noinspection PyMethodMayBeStatic
    def _preprocess_weather_forecast(self, response_text):
        df = pd.read_json(response_text)
        df = rename_column(df, consts.SOFT_M_WEATHER_T_COLUMN_NAME, consts.WEATHER_T_COLUMN_NAME)
        df = convert_date_and_time_to_timestamp(df, tzinfo=self._forecast_weather_server_timezone)
        df = round_timestamp(df)
        df = interpolate_passes_of_t(df, t_column_name=consts.WEATHER_T_COLUMN_NAME)
        df = remove_duplicates_by_timestamp(df)
        return df

    def _get_from_cache(self, start_date, end_date):
        return filter_by_timestamp(self._cached_weather_forecast_df, start_date, end_date).copy()

    def clean_old_cached_weather_forecast(self):
        datetime_now = datetime.now(tz=tzlocal())
        old_values_condition = self._cached_weather_forecast_df[consts.TIMESTAMP_COLUMN_NAME] < datetime_now
        old_values_idx = self._cached_weather_forecast_df[old_values_condition].index
        self._cached_weather_forecast_df.drop(old_values_idx, inplace=True)
