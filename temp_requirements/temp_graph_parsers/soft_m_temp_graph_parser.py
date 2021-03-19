import logging

import pandas as pd

import heating_system.temp_requirements_utils.constants.column_names
from ... import column_names
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
                heating_system.temp_requirements_utils.constants.column_names.SOFT_M_TEMP_GRAPH_WEATHER_TEMP: column_names.WEATHER_TEMP,
                heating_system.temp_requirements_utils.constants.column_names.SOFT_M_TEMP_GRAPH_TEMP_AT_HOME_IN: heating_system.temp_requirements_utils.constants.column_names.FORWARD_PIPE_TEMP,
                heating_system.temp_requirements_utils.constants.column_names.SOFT_M_TEMP_GRAPH_TEMP_AT_HOME_OUT: heating_system.temp_requirements_utils.constants.column_names.BACKWARD_PIPE_TEMP
            },
            inplace=True)
        return df
