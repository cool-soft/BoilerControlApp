import datetime
import logging

import pandas as pd
from dateutil.tz import gettz

import column_names
import time_tick
from preprocess_utils import round_datetime, parse_time
from .weather_data_parser import WeatherDataParser


class SoftMWeatherDataParser(WeatherDataParser):

    def __init__(self,
                 weather_data_timezone_name,
                 soft_m_weather_t_column_name,
                 soft_m_weather_date_column_name,
                 soft_m_weather_time_column_name):

        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of the service")

        self._soft_m_weather_t_column_name = soft_m_weather_t_column_name
        self._soft_m_weather_date_column_name = soft_m_weather_date_column_name
        self._soft_m_weather_time_column_name = soft_m_weather_time_column_name

        self._weather_data_timezone_name = weather_data_timezone_name
        self._time_parse_pattern = r"(?P<hour>\d\d):(?P<min>\d\d):(?P<sec>\d\d)"

    def parse_weather_data(self, weather_as_text):
        self._logger.debug("Parsing weather data")

        df = pd.read_json(weather_as_text)
        df.rename(
            columns={
                self._soft_m_weather_t_column_name: column_names.WEATHER_T
            },
            inplace=True
        )

        df = self._convert_date_and_time_to_timestamp(df)
        df[column_names.TIMESTAMP] = df[column_names.TIMESTAMP].apply(round_datetime)
        df = self._interpolate_passes_of_weather_data(df)
        return df

    def _convert_date_and_time_to_timestamp(self, df):
        datetime_list = []
        for _, row in df.iterrows():
            time_as_str = row[self._soft_m_weather_time_column_name]
            time = parse_time(time_as_str, self._time_parse_pattern)

            date = row[self._soft_m_weather_date_column_name].date()

            datetime_ = datetime.datetime.combine(date, time, tzinfo=gettz(self._weather_data_timezone_name))
            datetime_list.append(datetime_)

        df[column_names.TIMESTAMP] = datetime_list
        del df[self._soft_m_weather_date_column_name]
        del df[self._soft_m_weather_time_column_name]

        return df

    # noinspection PyMethodMayBeStatic
    def _interpolate_passes_of_weather_data(self, df):
        df.sort_values(by=column_names.TIMESTAMP, ignore_index=True, inplace=True)

        interpolated_values = []

        previous_datetime = None
        previous_t = None
        for index, row in df.iterrows():

            if previous_datetime is None:
                previous_datetime = row[column_names.TIMESTAMP]
                previous_t = row[column_names.WEATHER_T]
                continue

            next_datetime = row[column_names.TIMESTAMP]
            next_t = row[column_names.WEATHER_T]

            datetime_delta = next_datetime - previous_datetime
            if datetime_delta > time_tick.TIME_TICK:
                number_of_passes = int(datetime_delta // time_tick.TIME_TICK) - 1
                t_step = (next_t - previous_t) / number_of_passes
                for pass_n in range(1, number_of_passes + 1):
                    interpolated_datetime = previous_datetime + (time_tick.TIME_TICK * pass_n)
                    interpolated_t = previous_t + (t_step * pass_n)
                    interpolated_values.append({
                        column_names.TIMESTAMP: interpolated_datetime,
                        column_names.WEATHER_T: interpolated_t,
                    })

            previous_t = next_t
            previous_datetime = next_datetime

        df = df.append(interpolated_values)
        df.drop_duplicates(column_names.TIMESTAMP, inplace=True, ignore_index=True)
        df.sort_values(by=column_names.TIMESTAMP, ignore_index=True, inplace=True)

        return df
