from datetime import datetime

import pandas as pd
import numpy as np
from dateutil.tz import tzlocal
from dependency_injector import providers
# noinspection PyPackageRequirements
import matplotlib.pyplot as plt

import column_names
import preprocess_utils
import time_tick
from containers.services_containers.online_temp_graph_container import OnlineTempGraphContainer
from containers.services_containers.simple_boiler_temp_prediction_container import SimpleBoilerTempPredictionContainer
from containers.services_containers.simple_temp_requirements_container import SimpleTempRequirementsContainer
from services.weather_service.weather_service import WeatherService


class FakeWeatherService(WeatherService):

    def __init__(self):
        self._weather_temp_const = 0

    def set_weather_temp_const(self, weather_temp):
        self._weather_temp_const = weather_temp

    def get_weather(self, start_datetime: datetime, end_datetime: datetime) -> pd.DataFrame:
        start_datetime = preprocess_utils.round_datetime(start_datetime, time_tick.TIME_TICK.total_seconds())
        temps = []
        dates = []
        current_datetime = start_datetime
        while current_datetime <= end_datetime:
            temps.append(self._weather_temp_const)
            dates.append(current_datetime)
            current_datetime += time_tick.TIME_TICK

        return pd.DataFrame({
            column_names.TIMESTAMP: dates,
            column_names.WEATHER_TEMP: temps
        })


def main():
    min_weather_temp = -40
    max_weather_temp = 20
    weather_step = 1
    k_2 = 0.97

    temp_graph_service_config = {
        "server_address": "https://lysva.agt.town/",
        "update_interval": 86400
    }

    boiler_temp_prediction_service_config = {
        "home_min_temp_coefficient": 1,
        "homes_deltas_path": "../storage/homes_time_delta.csv",
        "temp_correlation_table_path": "../storage/temp_correlation_table.pickle"
    }

    temp_graph_container = OnlineTempGraphContainer(
        config=temp_graph_service_config
    )

    temp_requirements_container = SimpleTempRequirementsContainer(
        temp_graph_service=temp_graph_container.temp_graph_service,
        weather_service=providers.Singleton(FakeWeatherService)
    )

    boiler_temp_prediction_container = SimpleBoilerTempPredictionContainer(
        config=boiler_temp_prediction_service_config,
        temp_requirements_service=temp_requirements_container.temp_requirements_service
    )
    boiler_temp_prediction_container.init_resources()

    weather_service = temp_requirements_container.weather_service()
    boiler_temp_prediction_service = boiler_temp_prediction_container.boiler_temp_prediction_service()

    start_datetime = datetime.now(tzlocal())
    end_datetime = start_datetime + (time_tick.TIME_TICK * 30)

    boiler_temp_list, weather_temp_list = calc_boiler_temp(boiler_temp_prediction_service, end_datetime,
                                                           max_weather_temp, min_weather_temp, start_datetime,
                                                           weather_service, weather_step)
    boiler_temp_arr1 = np.array(boiler_temp_list)
    plt.plot(weather_temp_list, boiler_temp_list, label="К допуска: 1")

    boiler_temp_prediction_service.set_home_min_temp_coefficient(k_2)
    boiler_temp_list, weather_temp_list = calc_boiler_temp(boiler_temp_prediction_service, end_datetime,
                                                           max_weather_temp, min_weather_temp, start_datetime,
                                                           weather_service, weather_step)
    boiler_temp_arr2 = np.array(boiler_temp_list)
    plt.plot(weather_temp_list, boiler_temp_list, label=f"К допуска: {k_2}")

    delta = np.abs(boiler_temp_arr1 - boiler_temp_arr2)
    plt.plot(weather_temp_list, delta, label="Разница по модулю")

    plt.xlabel("Температура окр. среды")
    plt.ylabel("Температура бойлера")

    plt.grid()
    plt.legend()
    plt.show()


def calc_boiler_temp(boiler_temp_prediction_service, end_datetime, max_weather_temp, min_weather_temp, start_datetime,
                     weather_service, weather_step):
    weather_temp_list = []
    boiler_temp_list = []
    for i in range(min_weather_temp, max_weather_temp, weather_step):
        weather_service.set_weather_temp_const(i)
        boiler_temp_df = boiler_temp_prediction_service.get_need_boiler_temp(start_datetime, end_datetime)
        boiler_temp = boiler_temp_df[column_names.TEMP_AT_BOILER_OUT].to_list()

        weather_temp_list.append(i)
        boiler_temp_list.append(boiler_temp[0])
    return boiler_temp_list, weather_temp_list


if __name__ == '__main__':
    main()
