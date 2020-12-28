from datetime import datetime

import pandas as pd
from dateutil.tz import tzlocal
from dependency_injector import providers

import time_tick
import preprocess_utils
import column_names
from containers.services_containers.simple_temp_requirements_container import SimpleTempRequirementsContainer
from services.temp_graph_service.temp_graph_service import TempGraphService
from services.weather_service.weather_service import WeatherService


class FakeTempGraphService(TempGraphService):

    def get_temp_graph(self):
        return pd.DataFrame({
            column_names.WEATHER_TEMP: [11, 10, 9, -9, -10, -11],
            column_names.TEMP_AT_HOME_IN: [12, 11, 10, 28, 30, 32],
            column_names.TEMP_AT_HOME_OUT: [10, 8, 6, 22, 24, 26]
        })


class FakeWeatherService(WeatherService):

    def get_weather(self, start_datetime: datetime, end_datetime: datetime) -> pd.DataFrame:
        temps = [20, 10, 10.7, 10.1, 9, -10, -10.1, -10.7, -20]
        start_datetime = preprocess_utils.round_datetime(start_datetime, time_tick.TIME_TICK.total_seconds())
        dates = []
        for i in range(len(temps)):
            dates.append(start_datetime + (time_tick.TIME_TICK * i))
        return pd.DataFrame({
            column_names.TIMESTAMP: dates,
            column_names.WEATHER_TEMP: temps
        })


if __name__ == '__main__':

    temp_requirements_container = SimpleTempRequirementsContainer()

    fake_temp_graph_service = FakeTempGraphService()
    temp_requirements_container.temp_graph_service.override(providers.Object(fake_temp_graph_service))

    fake_weather_service = FakeWeatherService()
    temp_requirements_container.weather_service.override(providers.Object(fake_weather_service))

    start_datetime = datetime.now(tzlocal())
    end_datetime = start_datetime + (time_tick.TIME_TICK * 1000)

    temp_requirements_service = temp_requirements_container.temp_requirements_service()
    temp_requirements = temp_requirements_service.get_required_temp(start_datetime, end_datetime)

    weather_df = fake_weather_service.get_weather(start_datetime, end_datetime)

    assert len(weather_df) == len(temp_requirements)
    assert column_names.TIMESTAMP in temp_requirements.columns
    assert column_names.TEMP_AT_HOME_IN in temp_requirements.columns
    assert column_names.TEMP_AT_HOME_OUT in temp_requirements.columns

    weather_temp_list = weather_df[column_names.WEATHER_TEMP].to_list()
    required_temp_at_home_in_list = temp_requirements[column_names.TEMP_AT_HOME_IN].to_list()
    for weather_temp, required_tem_ath_home_in in zip(weather_temp_list, required_temp_at_home_in_list):
        print(f"Weather temp: {weather_temp}, Temp at home in: {required_tem_ath_home_in}")
