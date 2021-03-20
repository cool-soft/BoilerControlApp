import logging

import pandas as pd

from constants import column_names
from .temp_requirements_service import TempRequirementsService
from ..temp_graph_service.temp_graph_service import TempGraphService
from ..weather_service.weather_service import WeatherService


class SimpleTempRequirementsService(TempRequirementsService):

    def __init__(self,
                 temp_graph_service: TempGraphService = None,
                 weather_service: WeatherService = None,
                 temp_graph_requirements_calculator=None):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of the service")

        self._temp_graph_service = temp_graph_service
        self._weather_service = weather_service
        self._temp_graph_requirements_calculator = temp_graph_requirements_calculator

    def set_temp_graph_service(self, temp_graph_service):
        self._logger.debug("Temp graph service is set")
        self._temp_graph_service = temp_graph_service

    def set_weather_service(self, weather_service):
        self._logger.debug("Weather service is set")
        self._weather_service = weather_service

    def set_temp_graph_requirements_calculator(self, temp_graph_requirements_calculator):
        self._logger.debug("Temp graph requirements calculator is set")
        self._temp_graph_requirements_calculator = temp_graph_requirements_calculator

    def get_required_temp(self, start_datetime, end_datetime):
        self._logger.debug(f"Requested required temp from {start_datetime} to {end_datetime}")

        weather_df = self._weather_service.get_weather(start_datetime, end_datetime)
        weather_temp_arr = weather_df[column_names.WEATHER_TEMP].to_numpy()

        temp_graph = self._temp_graph_service.get_temp_graph()
        self._temp_graph_requirements_calculator.set_temp_graph(temp_graph)

        required_temp_at_home_in_list = []
        required_temp_at_home_out_list = []
        for weather_temp in weather_temp_arr:
            required_temp = self._temp_graph_requirements_calculator.get_temp_requirements_for_weather_temp(
                weather_temp
            )
            required_temp_at_home_in_list.append(required_temp[column_names.FORWARD_PIPE_COOLANT_TEMP])
            required_temp_at_home_out_list.append(required_temp[column_names.BACKWARD_PIPE_COOLANT_TEMP])

        temp_requirements_dates_list = weather_df[column_names.TIMESTAMP].to_list()
        temp_requirements_df = pd.DataFrame({
            column_names.TIMESTAMP: temp_requirements_dates_list,
            column_names.FORWARD_PIPE_COOLANT_TEMP: required_temp_at_home_in_list,
            column_names.BACKWARD_PIPE_COOLANT_TEMP: required_temp_at_home_out_list
        })

        return temp_requirements_df
