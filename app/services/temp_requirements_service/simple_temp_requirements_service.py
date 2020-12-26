import logging

import numpy as np
import pandas as pd

import column_names
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

        weather_df_len = len(weather_df)
        temp_requirements_arr = np.empty(shape=(weather_df_len,), dtype=np.float)
        weather_t_arr = weather_df[column_names.WEATHER_T].to_numpy()
        temp_graph = self._temp_graph_service.get_temp_graph()
        for i, weather_t in enumerate(weather_t_arr):
            required_temp = self._get_required_temp_at_home_in_by_temp_graph(weather_t, temp_graph)
            temp_requirements_arr[i] = required_temp

        temp_requirements_dates_list = weather_df[column_names.TIMESTAMP].to_list()
        temp_requirements_df = pd.DataFrame({
            column_names.TIMESTAMP: temp_requirements_dates_list,
            column_names.REQUIRED_T_AT_HOME_IN: temp_requirements_arr
        })

        return temp_requirements_df

    def _get_required_temp_at_home_in_by_temp_graph(self, weather_t, temp_graph):
        available_t_condition = temp_graph[column_names.WEATHER_T] <= weather_t
        available_t = temp_graph[available_t_condition]
        if not available_t.empty:
            required_t_at_home_in = available_t[column_names.REQUIRED_T_AT_HOME_IN].min()
        else:
            required_t_at_home_in = temp_graph[column_names.REQUIRED_T_AT_HOME_IN].max()
            self._logger.debug(f"Weather temp {weather_t} is not in temp graph. "
                               f"Need temp by temp graph is{required_t_at_home_in}")
        return required_t_at_home_in
