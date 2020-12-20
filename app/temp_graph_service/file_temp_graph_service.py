import os

import pandas as pd

from dataset_utils import data_consts
from .temp_graph_service import TempGraphService


class FileTempGraphService(TempGraphService):

    def __init__(self):
        self._temp_graph = None

    def get_required_t_at_home_in(self, weather_t):
        available_t_condition = self._temp_graph[data_consts.WEATHER_T_COLUMN_NAME] <= weather_t
        available_t = self._temp_graph[available_t_condition]
        if not available_t.empty:
            required_t_at_home_in = available_t[data_consts.REQUIRED_T_AT_HOME_IN_COLUMN_NAME].min()
        else:
            required_t_at_home_in = self._temp_graph[data_consts.REQUIRED_T_AT_HOME_IN_COLUMN_NAME].max()
        return required_t_at_home_in

    def get_temp_graph(self) -> pd.DataFrame:
        return self._temp_graph.copy()

    def load_temp_graph_from_file(self, temp_graph_path):
        temp_graph_path = os.path.abspath(temp_graph_path)
        self._temp_graph = pd.read_csv(temp_graph_path)

    @classmethod
    def create_service(cls, temp_graph_path):
        temp_graph_service = cls()
        temp_graph_service.load_temp_graph_from_file(temp_graph_path)
        return temp_graph_service
