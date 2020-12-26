import datetime
import logging
import re

import pandas as pd
from dateutil.tz import gettz

from preprocess_utils import round_timestamp, interpolate_passes_of_t
from .weather_data_parser import WeatherDataParser


class SoftMWeatherDataParser(WeatherDataParser):

    def __init__(self,
                 soft_m_weather_column_name,
                 soft_m_date_column_name,
                 soft_m_time_column_name,
                 timestamp_column_name,
                 weather_t_column_name,
                 weather_data_timezone_name):

        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of the service")

        self._soft_m_weather_column_name = soft_m_weather_column_name
        self._soft_m_time_column_name = soft_m_time_column_name
        self._soft_m_date_column_name = soft_m_date_column_name
        self._timestamp_column_name = timestamp_column_name
        self._weather_t_column_name = weather_t_column_name
        self._weather_data_timezone_name = weather_data_timezone_name
        self._time_parse_pattern = r"(?P<hour>\d\d):(?P<min>\d\d):(?P<sec>\d\d)"

    def parse_weather_data(self, weather_as_text):
        self._logger.debug("Parsing weather data")

        df = pd.read_json(weather_as_text)
        df.rename(
            columns={
                self._soft_m_weather_column_name: self._weather_t_column_name
            },
            inplace=True
        )

        df = self._convert_date_and_time_to_timestamp(df)
        df = round_timestamp(df)
        df = interpolate_passes_of_t(df, t_column_name=self._weather_t_column_name)
        df.drop_duplicates(self._timestamp_column_name, inplace=True, ignore_index=True)
        return df

    def _convert_date_and_time_to_timestamp(self, df):
        datetime_list = []
        for _, row in df.iterrows():
            time_as_str = row[self._soft_m_time_column_name]
            time = self._parse_time(time_as_str)

            date = row[self._soft_m_date_column_name].date()

            datetime_ = datetime.datetime.combine(date, time, tzinfo=gettz(self._weather_data_timezone_name))
            datetime_list.append(datetime_)

        df[self._timestamp_column_name] = datetime_list
        del df[self._soft_m_date_column_name]
        del df[self._soft_m_time_column_name]

        return df

    def _parse_time(self, time_as_str):
        parsed = re.match(self._time_parse_pattern, time_as_str)
        hour = int(parsed.group("hour"))
        minute = int(parsed.group("min"))
        second = int(parsed.group("sec"))
        time = datetime.time(hour=hour, minute=minute, second=second)
        return time

