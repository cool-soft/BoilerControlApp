import logging

import pandas as pd

from heating_system import column_names
from heating_system.preprocess_utils import arithmetic_round
from .temp_requirements_service import TempRequirementsService


class SimpleTempRequirementsService(TempRequirementsService):

    def __init__(self, temp_graph_service=None, weather_service=None):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of the service")

        self._temp_graph_service = temp_graph_service
        self._weather_service = weather_service

    def set_temp_graph_service(self, temp_graph_service):
        self._logger.debug("Temp graph service is set")
        self._temp_graph_service = temp_graph_service

    def set_weather_service(self, weather_service):
        self._logger.debug("Weather service is set")
        self._weather_service = weather_service

    def get_required_temp(self, start_datetime, end_datetime):
        self._logger.debug(f"Requested required temp from {start_datetime} to {end_datetime}")

        weather_df = self._weather_service.get_weather(start_datetime, end_datetime)

        required_temp_at_home_in_list = []
        required_temp_at_home_out_list = []
        weather_temp_arr = weather_df[column_names.WEATHER_TEMP].to_numpy()
        temp_graph = self._temp_graph_service.get_temp_graph()
        for weather_temp in weather_temp_arr:
            required_temp = self._get_required_temp_by_temp_graph(weather_temp, temp_graph)
            required_temp_at_home_in_list.append(required_temp[column_names.FORWARD_PIPE_TEMP])
            required_temp_at_home_out_list.append(required_temp[column_names.BACKWARD_PIPE_TEMP])

        temp_requirements_dates_list = weather_df[column_names.TIMESTAMP].to_list()
        temp_requirements_df = pd.DataFrame({
            column_names.TIMESTAMP: temp_requirements_dates_list,
            column_names.FORWARD_PIPE_TEMP: required_temp_at_home_in_list,
            column_names.BACKWARD_PIPE_TEMP: required_temp_at_home_out_list
        })

        return temp_requirements_df

    def _get_required_temp_by_temp_graph(self, weather_temp, temp_graph):
        weather_temp = arithmetic_round(weather_temp)

        available_temp_condition = temp_graph[column_names.WEATHER_TEMP] <= weather_temp
        available_temp = temp_graph[available_temp_condition]
        if not available_temp.empty:
            required_temp_idx = available_temp[column_names.WEATHER_TEMP].idxmax()

        else:
            required_temp_idx = temp_graph[column_names.WEATHER_TEMP].idxmin()
            self._logger.debug(f"Weather temp {weather_temp} is not in temp graph.")

        required_temp = temp_graph.loc[required_temp_idx]
        return required_temp.copy()
