import logging
from datetime import datetime

import pandas as pd
import requests
from dateutil.tz import tzlocal, gettz

from dataset_utils import data_consts
from dataset_utils.preprocess_utils import (
    rename_column,
    remove_duplicates_by_timestamp,
    convert_date_and_time_to_timestamp,
    filter_by_timestamp,
    get_min_max_timestamp,
    round_timestamp,
    interpolate_passes_of_t
)
from .weather_forecast_provider_config import WeatherForecastProviderConfig


class WeatherForecastProvider:

    def __init__(self):
        logging.debug("Initialization of WeatherForecastProvider")
        self._cached_forecast_df = pd.DataFrame()
        self._forecast_weather_server_timezone = None
        self._weather_forecast_server_address = None
        self._weather_forecast_update_interval = 1800
        self._cached_weather_forecast_last_update = None

    def set_server_timezone(self, server_timezone):
        self._forecast_weather_server_timezone = server_timezone

    def set_server_address(self, server_address):
        self._weather_forecast_server_address = server_address

    def set_update_interval(self, lifetime):
        self._weather_forecast_update_interval = lifetime

    def get_weather_forecast(self, start_datetime: datetime, end_datetime: datetime):
        logging.debug(f"Requested weather forecast from {start_datetime.isoformat()} to {end_datetime.isoformat()}")

        if self._is_datetime_not_in_cache(end_datetime) or \
                self._is_cached_forecast_expired():
            self._update_cache_from_server()

        return self._get_from_cache(start_datetime, end_datetime)

    def _is_datetime_not_in_cache(self, datetime_):
        logging.debug("Checking that requested datetime in cache")
        _, max_cached_datetime = get_min_max_timestamp(self._cached_forecast_df)

        if max_cached_datetime is None:
            logging.debug("Max cached datetime is None")
            return True

        if max_cached_datetime <= datetime_:
            logging.debug("Requested datetime is bigger that max cached datetime")
            return True

        logging.debug("Requested datetime in cache")
        return False

    def _is_cached_forecast_expired(self):
        logging.debug("Checking that cached weather forecast is not expired")

        if self._cached_weather_forecast_last_update is None:
            logging.debug("Weather forecast is never updated")
            return True

        datetime_now = datetime.now(tzlocal())
        weather_forecast_lifetime = (datetime_now - self._cached_weather_forecast_last_update)
        if weather_forecast_lifetime.total_seconds() > self._weather_forecast_update_interval:
            logging.debug("Cached weather forecast is expired")
            return True

        logging.debug("Cached weather forecast is not expired")
        return False

    def _update_cache_from_server(self):
        logging.debug("Updating weather forecast")
        data = self._get_forecast_from_server()
        new_weather_forecast_df = self._preprocess_forecast(data)
        self._cached_forecast_df = new_weather_forecast_df
        self._cached_weather_forecast_last_update = datetime.now(tzlocal())
        logging.debug("Weather forecast is updated")

    # noinspection PyMethodMayBeStatic
    def _get_forecast_from_server(self):
        logging.debug(f"Requesting weather forecast from server {self._weather_forecast_server_address}")
        url = f"{self._weather_forecast_server_address}/JSON/"
        # noinspection SpellCheckingInspection
        params = {
            "method": "getPrognozT"
        }
        response = requests.get(url, params=params)
        logging.debug(f"Weather forecast is loaded. Response status code is {response.status_code}")
        return response.text

    # noinspection PyMethodMayBeStatic
    def _preprocess_forecast(self, response_text):
        logging.debug("Preprocessing weather forecast")
        df = pd.read_json(response_text)
        df = rename_column(df, data_consts.SOFT_M_WEATHER_T_COLUMN_NAME, data_consts.WEATHER_T_COLUMN_NAME)
        df = convert_date_and_time_to_timestamp(df, tzinfo=self._forecast_weather_server_timezone)
        df = round_timestamp(df)
        df = interpolate_passes_of_t(df, t_column_name=data_consts.WEATHER_T_COLUMN_NAME)
        df = remove_duplicates_by_timestamp(df)
        logging.debug("Weather forecast is preprocessed")
        return df

    def _get_from_cache(self, start_datetime, end_datetime):
        logging.debug("Taking weather forecast from cache")
        return filter_by_timestamp(self._cached_forecast_df, start_datetime, end_datetime).copy()

    @classmethod
    def from_config(cls, config: WeatherForecastProviderConfig):
        weather_forecast_provider = cls()
        weather_forecast_provider.set_server_address(config.server_address)
        weather_forecast_provider.set_server_timezone(gettz(config.server_timezone))
        weather_forecast_provider.set_update_interval(config.update_interval)
        return weather_forecast_provider
