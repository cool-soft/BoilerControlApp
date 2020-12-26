import logging
import os
import pickle

import pandas as pd
from dependency_injector import resources


class OptimizedTTableResource(resources.Resource):

    def init(self, optimized_temp_table_path) -> pd.DataFrame:
        logger = logging.getLogger(self.__class__.__name__)
        optimized_temp_table_path = os.path.abspath(optimized_temp_table_path)
        logger.debug(f"Loading optimized temp table from {optimized_temp_table_path}")
        with open(optimized_temp_table_path, "rb") as f:
            optimized_t_table = pickle.load(f)
        return optimized_t_table

    def shutdown(self, optimized_temp_table: pd.DataFrame):
        pass
