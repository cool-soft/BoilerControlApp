from datetime import datetime

import pandas as pd
from dateutil.tz import tzlocal

import data_consts
from services.temp_graph_service.simple_temp_graph_service import SimpleTempGraphService
from services.temp_requirements_service.simple_temp_requirements_service import SimpleTempRequirementsService
from services.weather_service.weather_service import WeatherService


def main():
    # noinspection PyShadowingNames
    class FakeWeatherService(WeatherService):

        def get_weather(self, start_datetime: datetime, end_datetime: datetime) -> pd.DataFrame:
            fake_weather_info = pd.DataFrame({
                data_consts.TIMESTAMP_COLUMN_NAME: [
                    start_datetime,
                    start_datetime + data_consts.TIME_TICK,
                    start_datetime + (2 * data_consts.TIME_TICK),
                    start_datetime + (3 * data_consts.TIME_TICK),
                ],
                data_consts.WEATHER_T_COLUMN_NAME: [
                    10,
                    1,
                    -1,
                    -10
                ]
            })
            return fake_weather_info

    fake_temp_graph = pd.DataFrame({
        data_consts.WEATHER_T_COLUMN_NAME: [1, -1],
        data_consts.REQUIRED_T_AT_HOME_IN_COLUMN_NAME: [20, 30]
    })

    temp_graph_service = SimpleTempGraphService()
    temp_graph_service.set_temp_graph(fake_temp_graph)
    weather_service = FakeWeatherService()

    temp_requirements_service = SimpleTempRequirementsService()
    temp_requirements_service.set_temp_graph_service(temp_graph_service)
    temp_requirements_service.set_weather_service(weather_service)

    start_datetime = datetime.now(tz=tzlocal())
    end_datetime = start_datetime + (5 * data_consts.TIME_TICK)
    temp_requirements = temp_requirements_service.get_required_temp(start_datetime, end_datetime)

    print(temp_requirements)


if __name__ == '__main__':
    main()
