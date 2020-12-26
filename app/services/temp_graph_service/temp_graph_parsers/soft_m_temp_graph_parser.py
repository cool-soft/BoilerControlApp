import logging

import pandas as pd

import column_names
from .temp_graph_parser import TempGraphParser


class SoftMTempGraphParser(TempGraphParser):

    def __init__(self,
                 soft_m_weather_column_name,
                 soft_m_required_t_at_home_in_column_name,
                 soft_m_required_t_at_home_out_column_name):

        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of the service")

        self._soft_m_weather_column_name = soft_m_weather_column_name
        self._soft_m_required_t_at_home_in_column_name = soft_m_required_t_at_home_in_column_name
        self._soft_m_required_t_at_home_out_column_name = soft_m_required_t_at_home_out_column_name

    def parse_temp_graph(self, temp_graph_as_text):
        self._logger.debug("Parsing temp graph")

        df = pd.read_json(temp_graph_as_text)
        df.rename(
            columns={
                self._soft_m_weather_column_name: column_names.WEATHER_T,
                self._soft_m_required_t_at_home_in_column_name: column_names.REQUIRED_T_AT_HOME_IN,
                self._soft_m_required_t_at_home_out_column_name: column_names.REQUIRED_T_AT_HOME_OUT
            },
            inplace=True)
        return df
