import pandas as pd
from dateutil.tz import tzlocal
from dependency_injector import providers

from boiler.constants import column_names
from boiler.constants import time_tick
from backend.containers.services_containers.temp_requirements_container import TempRequirementsContainer
from boiler.temp_graph.repository.temp_graph_repository import TempGraphRepository
from boiler.weater_info.repository.online_soft_m_weather_forecast_repository import WeatherRepository


class FakeTempGraphRepository(TempGraphRepository):

    # noinspection PyMethodMayBeStatic
    def get_temp_graph(self):
        return pd.DataFrame({
            column_names.WEATHER_TEMP: [11, 10, 9, -9, -10, -11],
            column_names.FORWARD_PIPE_COOLANT_TEMP: [12, 11, 10, 28, 30, 32],
            column_names.BACKWARD_PIPE_COOLANT_TEMP: [10, 8, 6, 22, 24, 26]
        })


class FakeWeatherRepository(WeatherRepository):

    # noinspection PyMethodMayBeStatic,PyShadowingNames,PyUnusedLocal
    def get_weather_info(self,
                         start_datetime: pd.Timestamp = None,
                         end_datetime: pd.Timestamp = None) -> pd.DataFrame:
        start_datetime = start_datetime.ceil(f"{int(time_tick.TIME_TICK.total_seconds())}s")

        temps = [20, 10, 10.7, 10.1, 9, -10, -10.1, -10.7, -20]
        dates = []
        for i in range(len(temps)):
            dates.append(start_datetime + (time_tick.TIME_TICK * i))

        return pd.DataFrame({
            column_names.TIMESTAMP: dates,
            column_names.WEATHER_TEMP: temps
        })


if __name__ == '__main__':

    temp_requirements_container = TempRequirementsContainer()

    fake_temp_graph_service = FakeTempGraphRepository()
    temp_requirements_container.temp_graph_service.override(providers.Object(fake_temp_graph_service))

    fake_weather_service = FakeWeatherRepository()
    temp_requirements_container.weather_service.override(providers.Object(fake_weather_service))

    start_datetime = pd.Timestamp.now(tzlocal())
    end_datetime = start_datetime + (time_tick.TIME_TICK * 1000)

    temp_requirements_service = temp_requirements_container.temp_requirements_service()
    temp_requirements_df = temp_requirements_service.predict_control_actions_async(
        start_datetime, end_datetime
    )

    weather_df = fake_weather_service.get_weather_info(start_datetime, end_datetime)

    assert len(weather_df) == len(temp_requirements_df)
    assert column_names.TIMESTAMP in temp_requirements_df.columns
    assert column_names.FORWARD_PIPE_COOLANT_TEMP in temp_requirements_df.columns
    assert column_names.BACKWARD_PIPE_COOLANT_TEMP in temp_requirements_df.columns

    weather_temp_list = weather_df[column_names.WEATHER_TEMP].to_list()
    required_temp_at_home_in_list = temp_requirements_df[column_names.FORWARD_PIPE_COOLANT_TEMP].to_list()
    for weather_temp, required_tem_ath_home_in in zip(weather_temp_list, required_temp_at_home_in_list):
        print(f"Weather temp: {weather_temp}, Temp at home in: {required_tem_ath_home_in}")
