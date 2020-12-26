import logging
from datetime import datetime

import pandas as pd
import requests
from dateutil.tz import tzlocal

from preprocess_utils import (
    filter_by_timestamp,
    get_min_max_timestamp
)
from .weather_service import WeatherService


class OnlineSoftMWeatherService(WeatherService):

    def __init__(self, server_address=None, update_interval=1800, weather_data_parser=None):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of the service")

        self._weather_data_server_address = server_address
        self._weather_data_update_interval = update_interval

        self._cached_weather_df = pd.DataFrame()
        self._cached_weather_data_last_update = None

        self._weather_data_parser = weather_data_parser

    def set_server_address(self, server_address):
        self._logger.debug(f"Server address is set to {server_address}")
        self._weather_data_server_address = server_address

    def set_update_interval(self, update_interval):
        self._logger.debug(f"Weather update interval is set to {update_interval}")
        self._weather_data_update_interval = update_interval

    def get_weather(self, start_datetime: datetime, end_datetime: datetime):
        self._logger.debug(f"Requested weather info from {start_datetime} to {end_datetime}")

        if self._is_datetime_not_in_cache(end_datetime) or \
                self._is_cached_forecast_expired():
            self._update_cache_from_server()

        return self._get_from_cache(start_datetime, end_datetime)

    def _is_datetime_not_in_cache(self, datetime_):
        self._logger.debug("Checking that requested datetime in cache")
        _, max_cached_datetime = get_min_max_timestamp(self._cached_weather_df)

        if max_cached_datetime is None:
            self._logger.debug("Max cached datetime is None")
            return True

        if max_cached_datetime <= datetime_:
            self._logger.debug("Requested datetime is bigger that max cached datetime")
            return True

        self._logger.debug("Requested datetime in cache")
        return False

    def _is_cached_forecast_expired(self):
        self._logger.debug("Checking that cached weather forecast is not expired")

        if self._cached_weather_data_last_update is None:
            self._logger.debug("Weather forecast is never updated")
            return True

        datetime_now = datetime.now(tzlocal())
        weather_forecast_lifetime = (datetime_now - self._cached_weather_data_last_update)
        if weather_forecast_lifetime.total_seconds() > self._weather_data_update_interval:
            self._logger.debug("Cached weather forecast is expired")
            return True

        self._logger.debug("Cached weather forecast is not expired")
        return False

    def _update_cache_from_server(self):
        self._logger.debug("Updating weather forecast from server")
        data = self._get_forecast_from_server()
        self._cached_weather_df = self._weather_data_parser.parse_weather_data(data)
        self._cached_weather_data_last_update = datetime.now(tzlocal())

    # noinspection PyMethodMayBeStatic
    def _get_forecast_from_server(self):
        self._logger.debug(f"Requesting weather forecast from server {self._weather_data_server_address}")
        url = f"{self._weather_data_server_address}/JSON/"
        # noinspection SpellCheckingInspection
        params = {
            "method": "getPrognozT"
        }
        response = requests.get(url, params=params)
        self._logger.debug(f"Weather forecast is loaded. Response status code is {response.status_code}")
        return response.text

    def _get_from_cache(self, start_datetime, end_datetime):
        self._logger.debug("Taking weather forecast from cache")
        return filter_by_timestamp(self._cached_weather_df, start_datetime, end_datetime).copy()
