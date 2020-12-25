import logging
import os

from dependency_injector import resources
import pandas as pd

from dataset_utils.io_utils import load_dataframe


class OptimizedTTableResource(resources.Resource):

    def init(self, optimized_temp_table_path) -> pd.DataFrame:
        logger = logging.getLogger(self.__class__.__name__)
        optimized_temp_table_path = os.path.abspath(optimized_temp_table_path)
        logger.debug(f"Loading optimized temp table from {optimized_temp_table_path}")
        optimized_t_table = load_dataframe(optimized_temp_table_path)
        return optimized_t_table

    def shutdown(self, optimized_temp_table: pd.DataFrame):
        pass
