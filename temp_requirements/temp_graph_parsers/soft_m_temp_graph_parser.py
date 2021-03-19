import logging

import pandas as pd

import temp_requirements.constants.column_names
from heating_system import column_names
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
                temp_requirements.constants.column_names.SOFT_M_TEMP_GRAPH_WEATHER_TEMP: column_names.WEATHER_TEMP,
                temp_requirements.constants.column_names.SOFT_M_TEMP_GRAPH_TEMP_AT_HOME_IN: temp_requirements.constants.column_names.FORWARD_PIPE_TEMP,
                temp_requirements.constants.column_names.SOFT_M_TEMP_GRAPH_TEMP_AT_HOME_OUT: temp_requirements.constants.column_names.BACKWARD_PIPE_TEMP
            },
            inplace=True)
        return df
