import logging

import pandas as pd
import requests

from ...constants import column_names
from boiler.weater_info.interpolators.weather_data_interpolator import WeatherDataInterpolator
from boiler.weater_info.parsers.weather_data_parser import WeatherDataParser
from .weather_provider import WeatherProvider


class OnlineSoftMWeatherForecastProvider(WeatherProvider):

    def __init__(self,
                 server_address="https://lysva.agt.town/",
                 weather_data_parser: WeatherDataParser = None,
                 weather_data_interpolator: WeatherDataInterpolator = None):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of the service")

        self._weather_data_server_address = server_address
        self._weather_data_parser = weather_data_parser
        self._weather_data_interpolator = weather_data_interpolator

    def set_server_address(self, server_address):
        self._logger.debug(f"Server address is set to {server_address}")
        self._weather_data_server_address = server_address

    def set_weather_data_parser(self, weather_data_parser: WeatherDataParser):
        self._logger.debug("Weather data parser is set")
        self._weather_data_parser = weather_data_parser

    def get_weather(self, start_datetime: pd.Timestamp = None, end_datetime: pd.Timestamp = None):
        self._logger.debug(f"Requested weather info from {start_datetime} to {end_datetime}")

        data = self._get_forecast_from_server()
        weather_df = self._weather_data_parser.parse_weather_data(data)
        weather_df = self._weather_data_interpolator.interpolate_weather_data(weather_df)

        if start_datetime is not None:
            weather_df = weather_df[weather_df[column_names.TIMESTAMP] >= start_datetime]
        if end_datetime is not None:
            weather_df = weather_df[weather_df[column_names.TIMESTAMP] <= end_datetime]

        return weather_df

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
