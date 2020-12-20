import numpy as np
import pandas as pd

from dataset_utils import data_consts
from .temp_requirements_service import TempRequirementsService


class SimpleTempRequirementsService(TempRequirementsService):

    def __init__(self):
        self._temp_graph = None
        self._weather_service = None

    def set_temp_graph(self, temp_graph):
        self._temp_graph = temp_graph

    def set_weather_service(self, weather_service):
        self._weather_service = weather_service

    def get_required_temp(self, start_datetime, end_datetime):
        weather_df = self._weather_service.get_weather(start_datetime, end_datetime)

        weather_df_len = len(weather_df)
        temp_requirements_arr = np.empty(shape=(weather_df_len,), dtype=np.float)
        weather_t_arr = weather_df[data_consts.WEATHER_T_COLUMN_NAME].to_numpy()
        for i, weather_t in enumerate(weather_t_arr):
            required_temp = self._get_required_temp_at_home_in_by_temp_graph(weather_t)
            temp_requirements_arr[i] = required_temp

        temp_requirements_dates_list = weather_df[data_consts.TIMESTAMP_COLUMN_NAME].to_list()
        temp_requirements_df = pd.DataFrame({
            data_consts.TIMESTAMP_COLUMN_NAME: temp_requirements_dates_list,
            data_consts.REQUIRED_T_AT_HOME_IN_COLUMN_NAME: temp_requirements_arr
        })

        return temp_requirements_df

    def _get_required_temp_at_home_in_by_temp_graph(self, weather_t):
        available_t_condition = self._temp_graph[data_consts.WEATHER_T_COLUMN_NAME] <= weather_t
        available_t = self._temp_graph[available_t_condition]
        if not available_t.empty:
            required_t_at_home_in = available_t[data_consts.REQUIRED_T_AT_HOME_IN_COLUMN_NAME].min()
        else:
            required_t_at_home_in = self._temp_graph[data_consts.REQUIRED_T_AT_HOME_IN_COLUMN_NAME].max()
        return required_t_at_home_in

    @classmethod
    def create_service(cls, temp_graph, weather_service):
        temp_requirements_service = cls()
        temp_requirements_service.set_temp_graph(temp_graph)
        temp_requirements_service.set_weather_service(weather_service)
        return temp_requirements_service
