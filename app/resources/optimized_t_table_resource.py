import os

from dependency_injector import resources
import pandas as pd

from dataset_utils.io_utils import load_dataframe


class OptimizedTTableResource(resources.Resource):

    def init(self, optimized_t_table_path) -> pd.DataFrame:
        optimized_t_table_path = os.path.abspath(optimized_t_table_path)
        optimized_t_table = load_dataframe(optimized_t_table_path)
        return optimized_t_table

    def shutdown(self, optimized_t_table: pd.DataFrame):
        pass
