import logging
import os

import pandas as pd
from dependency_injector import resources


class TempCorrelationTable(resources.Resource):

    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of Resource")

    def init(self, temp_correlation_table_path) -> pd.DataFrame:
        temp_correlation_table_path = os.path.abspath(temp_correlation_table_path)
        self._logger.debug(f"Loading optimized temp table from {temp_correlation_table_path}")

        temp_correlation_table = pd.read_pickle(temp_correlation_table_path)

        return temp_correlation_table

    def shutdown(self, optimized_temp_table: pd.DataFrame):
        pass
