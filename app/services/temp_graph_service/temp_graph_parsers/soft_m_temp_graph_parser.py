import logging

import pandas as pd

import column_names
from .temp_graph_parser import TempGraphParser


class SoftMTempGraphParser(TempGraphParser):

    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of the service")

    def parse_temp_graph(self, temp_graph_as_text):
        self._logger.debug("Parsing temp graph")

        df = pd.read_json(temp_graph_as_text)
        df.rename(
            columns={
                column_names.SOFT_M_TEMP_GRAPH_WEATHER_TEMP: column_names.WEATHER_TEMP,
                column_names.SOFT_M_TEMP_GRAPH_REQUIRED_TEMP_AT_HOME_IN: column_names.REQUIRED_TEMP_AT_HOME_IN,
                column_names.SOFT_M_TEMP_GRAPH_REQUIRED_TEMP_AT_HOME_OUT: column_names.REQUIRED_TEMP_AT_HOME_OUT
            },
            inplace=True)
        return df
