import logging
import os

import pandas as pd
from dependency_injector import resources


class TempCorrelationTable(resources.Resource):

    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of Resource")

    def init(self, filepath: str) -> pd.DataFrame:
        filepath = os.path.abspath(filepath)
        self._logger.debug(f"Loading correlation temp table from {filepath}")
        temp_correlation_table = pd.read_pickle(filepath)
        return temp_correlation_table

    def shutdown(self, correlation_table: pd.DataFrame):
        pass
