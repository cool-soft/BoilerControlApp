import numpy as np
import pandas as pd
from dateutil.tz import tzlocal
from dependency_injector import providers

from boiler_constants import column_names
from boiler_constants import time_tick
from containers.services_containers.online_temp_graph_container import OnlineTempGraphContainer
from containers.services_containers.corr_table_boiler_temp_prediction_container \
    import CorrTableBoilerTempPredictionContainer
from containers.services_containers.simple_temp_requirements_container import SimpleTempRequirementsContainer
from boiler_weater_info.providers.online_soft_m_weather_forecast_provider import WeatherProvider


# noinspection PyPackageRequirements
# import matplotlib.pyplot as plt


class FakeWeatherProvider(WeatherProvider):

    def __init__(self):
        self._weather_temp_const = 0

    def set_weather_temp_const(self, weather_temp):
        self._weather_temp_const = weather_temp

    def get_weather(self, start_datetime: pd.Timestamp = None, end_datetime: pd.Timestamp = None) -> pd.DataFrame:
        start_datetime = start_datetime.ceil(f"{int(time_tick.TIME_TICK.total_seconds())}s")

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


def calc_boiler_temp(boiler_temp_prediction_service, end_datetime, max_weather_temp, min_weather_temp, start_datetime,
                     weather_service, weather_step):
    weather_temp_list = []
    boiler_temp_list = []
    current_temp = min_weather_temp
    while current_temp <= max_weather_temp:
        weather_service.set_weather_temp_const(current_temp)
        boiler_temp_df = boiler_temp_prediction_service.get_need_boiler_temp(start_datetime, end_datetime)
        boiler_temp = boiler_temp_df[column_names.FORWARD_PIPE_COOLANT_TEMP].to_list()

        weather_temp_list.append(current_temp)
        boiler_temp_list.append(boiler_temp[0])

        current_temp += weather_step

    return boiler_temp_list, weather_temp_list


def calc_mean_gradient(gradient, x):
    result_x = []
    result_y = []
    for i in range(len(gradient)-1):
        result_x.append((x[i], x[i+1]))
        # noinspection PyUnresolvedReferences
        result_y.append(np.mean((gradient[i], gradient[i+1])))

    return result_x, result_y


def main():
    min_weather_temp = -30
    max_weather_temp = 5
    weather_step = 0.5

    temp_graph_service_config = {
        "update_interval": 86400
    }

    boiler_temp_prediction_service_config = {
        "home_min_temp_coefficient": 0.97,
        "homes_deltas_path": "dev_data/storage/homes_time_delta.csv",
        "temp_correlation_table_path": "dev_data/storage/temp_correlation_table.pickle"
    }

    temp_graph_container = OnlineTempGraphContainer(
        config=temp_graph_service_config
    )

    temp_requirements_container = SimpleTempRequirementsContainer(
        temp_graph_service=temp_graph_container.temp_graph_service,
        weather_service=providers.Singleton(FakeWeatherProvider)
    )

    boiler_temp_prediction_container = CorrTableBoilerTempPredictionContainer(
        config=boiler_temp_prediction_service_config,
        temp_requirements_service=temp_requirements_container.temp_requirements_service
    )
    boiler_temp_prediction_container.init_resources()

    weather_service = temp_requirements_container.weather_service()
    boiler_temp_prediction_service = boiler_temp_prediction_container.boiler_temp_prediction_service()

    start_datetime = pd.Timestamp.now(tzlocal())
    end_datetime = start_datetime + (time_tick.TIME_TICK * 30)

    boiler_temp_list, weather_temp_list = calc_boiler_temp(boiler_temp_prediction_service, end_datetime,
                                                           max_weather_temp, min_weather_temp, start_datetime,
                                                           weather_service, weather_step)
    gradient = np.gradient(boiler_temp_list, weather_temp_list)

    # noinspection PyUnresolvedReferences
    print(f"Mean: {np.mean(gradient):6.3}")
    # noinspection PyUnresolvedReferences
    print(f"Var: {np.var(gradient):6.3}")

    # res_x, res_y = calc_mean_gradient(gradient, weather_temp_list)
    # for x, y in zip(res_x, res_y):
    #     print(f"от {x[0]:3} до {x[1]:3}: {y:5.3}")
    #
    # plt.plot(weather_temp_list, gradient, label="GRADIENT")
    # plt.xlabel("Температура окр. среды")
    # plt.ylabel("Градиент температуры бойлера")
    #
    # plt.grid()
    # plt.legend()
    # plt.show()


if __name__ == '__main__':
    main()
