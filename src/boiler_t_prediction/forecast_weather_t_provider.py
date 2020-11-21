
from datetime import datetime

import consts
from dataset_utils.preprocess_utils import (
    rename_column,
    remove_duplicates_by_timestamp,
    convert_date_and_time_to_timestamp,
    filter_by_timestamp,
    get_min_max_timestamp,
    round_timestamp,
    round_datetime,
    interpolate_passes_of_t
)

import pandas as pd
import requests


class WeatherForecastProvider:

    def __init__(self):
        self._cached_weather_forecast_df = pd.DataFrame()
        self._forecast_weather_server_timezone = None
        self._forecast_weather_server_address = None

    def set_weather_forecast_server_timezone(self, timezone):
        self._forecast_weather_server_timezone = timezone

    def set_weather_forecast_server_address(self, server_address):
        self._forecast_weather_server_address = server_address

    def get_weather_forecast(self, min_date, max_date):
        min_date = round_datetime(min_date)
        max_date = round_datetime(max_date)

        if self._is_requested_datetime_not_in_cache(max_date):
            self._update_cache_from_server()

        return self._get_from_cache(min_date, max_date)

    def _is_requested_datetime_not_in_cache(self, requested_datetime):
        _, max_cached_datetime = get_min_max_timestamp(self._cached_weather_forecast_df)
        if max_cached_datetime is None:
            return True
        if max_cached_datetime <= requested_datetime:
            return True
        return False

    def _update_cache_from_server(self):
        data = self._get_weather_forecast_from_server()
        dataframe = self._preprocess_weather_forecast(data)
        self._update_cache(dataframe)

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

    def _update_cache(self, new_weather_forecast_df):
        new_weather_forecast_cache = pd.concat(
            (self._cached_weather_forecast_df, new_weather_forecast_df),
            ignore_index=True
        )
        new_weather_forecast_cache = remove_duplicates_by_timestamp(new_weather_forecast_cache)
        self._cached_weather_forecast_df = new_weather_forecast_cache

    def _get_from_cache(self, start_date, end_date):
        return filter_by_timestamp(self._cached_weather_forecast_df, start_date, end_date).copy()

    def compact_cache(self):
        # TODO: timezone
        datetime_now = round_datetime(datetime.now())
        old_values_condition = self._cached_weather_forecast_df[consts.TIMESTAMP_COLUMN_NAME] < datetime_now
        old_values_idx = self._cached_weather_forecast_df[old_values_condition].index
        self._cached_weather_forecast_df.drop(old_values_idx, inplace=True)
