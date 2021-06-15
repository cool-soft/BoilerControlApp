import os

import pandas as pd
from dependency_injector import resources

from backend.logger import logger


class TempCorrelationTable(resources.Resource):

    def init(self, filepath: str) -> pd.DataFrame:
        filepath = os.path.abspath(filepath)
        logger.debug(f"Loading correlation temp table from {filepath}")
        temp_correlation_table = pd.read_pickle(filepath)
        return temp_correlation_table

    def shutdown(self, correlation_table: pd.DataFrame):
        pass
