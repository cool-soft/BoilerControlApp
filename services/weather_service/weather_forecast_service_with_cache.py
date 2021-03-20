import logging

import pandas as pd
from dateutil.tz import tzlocal

from weather_data.constants import column_names
from weather_data.providers.weather_provider import WeatherProvider
from .weather_forecast_service import WeatherForecastService


class WeatherForecastServiceWithCache(WeatherForecastService):

    def __init__(self,
                 weather_forecast_provider: WeatherProvider = None,
                 update_interval=1800):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of the service")

        self._weather_forecast_provider = weather_forecast_provider
        self._weather_cache_update_interval = update_interval
        self._weather_cache_df = pd.DataFrame()
        self._weather_cache_last_update = None

    def set_update_interval(self, update_interval):
        self._logger.debug(f"Weather update interval is set to {update_interval}")
        self._weather_cache_update_interval = update_interval

    def set_weather_provider(self, weather_provider: WeatherProvider):
        self._logger.debug("Weather provider is set")
        self._weather_forecast_provider = weather_provider

    def get_weather_forecast(self, start_datetime: pd.Timestamp, end_datetime: pd.Timestamp) -> pd.DataFrame:
        self._logger.debug(f"Requested weather forecast from {start_datetime} to {end_datetime}")

        if self._is_datetime_not_in_cache(end_datetime) or \
                self._is_cached_forecast_expired():
            self._update_cache_from_server()

        return self._get_from_cache(start_datetime, end_datetime)

    def _is_datetime_not_in_cache(self, datetime_):
        self._logger.debug("Checking that requested datetime in cache")
        max_cached_datetime = self._get_max_cached_datetime()

        if max_cached_datetime is None:
            self._logger.debug("Max cached datetime is None")
            return True

        if max_cached_datetime <= datetime_:
            self._logger.debug("Requested datetime is bigger that max cached datetime")
            return True

        self._logger.debug("Requested datetime in cache")
        return False

    def _get_max_cached_datetime(self):
        if self._weather_cache_df.empty:
            return None
        max_date = self._weather_cache_df[column_names.TIMESTAMP].max()
        return max_date

    def _is_cached_forecast_expired(self):
        self._logger.debug("Checking that cached weather forecast is not expired")

        if self._weather_cache_last_update is None:
            self._logger.debug("Weather forecast is never updated")
            return True

        datetime_now = pd.Timestamp.now(tz=tzlocal())
        weather_forecast_lifetime = (datetime_now - self._weather_cache_last_update)
        if weather_forecast_lifetime.total_seconds() > self._weather_cache_update_interval:
            self._logger.debug("Cached weather forecast is expired")
            return True

        self._logger.debug("Cached weather forecast is not expired")
        return False

    def _update_cache_from_server(self):
        self._logger.debug("Updating weather forecast from server")

        weather_df = self._weather_forecast_provider.get_weather()
        self._weather_cache_df = weather_df
        self._weather_cache_last_update = pd.Timestamp.now(tz=tzlocal())

    def _get_from_cache(self, start_datetime, end_datetime):
        self._logger.debug("Taking weather forecast from cache")
        df = self._weather_cache_df[
            (self._weather_cache_df[column_names.TIMESTAMP] >= start_datetime) &
            (self._weather_cache_df[column_names.TIMESTAMP] < end_datetime)
            ]
        return df.copy()
