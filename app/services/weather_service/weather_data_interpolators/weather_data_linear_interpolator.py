import logging

import pandas as pd

import column_names
import time_tick
from preprocess_utils import round_datetime
from .weather_data_interpolator import WeatherDataInterpolator


class WeatherDataLinearInterpolator(WeatherDataInterpolator):

    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of the service")

        self._time_tick = time_tick.TIME_TICK

    def interpolate_weather_data(self, weather_data: pd.DataFrame) -> pd.DataFrame:
        self._logger.debug("Requested weather data interpolating")

        weather_data[column_names.TIMESTAMP] = weather_data[column_names.TIMESTAMP].apply(
            lambda datetime_: round_datetime(datetime_, self._time_tick.total_seconds())
        )
        weather_data.drop_duplicates(column_names.TIMESTAMP, inplace=True, ignore_index=True)
        weather_data = self._interpolate_passes_of_weather_data(weather_data)
        return weather_data

    # noinspection PyMethodMayBeStatic
    def _interpolate_passes_of_weather_data(self, weather_data: pd.DataFrame):
        self._logger.debug("Interpolating passes of weather data")

        weather_data.sort_values(by=column_names.TIMESTAMP, ignore_index=True, inplace=True)
        interpolated_values = []

        previous_datetime = None
        previous_t = None
        for index, row in weather_data.iterrows():

            if previous_datetime is None:
                previous_datetime = row[column_names.TIMESTAMP]
                previous_t = row[column_names.WEATHER_T]
                continue

            next_datetime = row[column_names.TIMESTAMP]
            next_t = row[column_names.WEATHER_T]

            datetime_delta = next_datetime - previous_datetime
            if datetime_delta > self._time_tick:
                number_of_passes = int(datetime_delta // self._time_tick) - 1
                t_step = (next_t - previous_t) / number_of_passes
                for pass_n in range(1, number_of_passes + 1):
                    interpolated_datetime = previous_datetime + (self._time_tick * pass_n)
                    interpolated_t = previous_t + (t_step * pass_n)
                    interpolated_values.append({
                        column_names.TIMESTAMP: interpolated_datetime,
                        column_names.WEATHER_T: interpolated_t,
                    })

            previous_t = next_t
            previous_datetime = next_datetime

        weather_data = weather_data.append(interpolated_values)
        weather_data.sort_values(by=column_names.TIMESTAMP, ignore_index=True, inplace=True)

        return weather_data
