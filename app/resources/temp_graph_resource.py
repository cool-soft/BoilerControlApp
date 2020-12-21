import os

from dependency_injector import resources
import pandas as pd


class TempGraphResource(resources.Resource):

    def init(self, temp_graph_path) -> pd.DataFrame:
        temp_graph_path = os.path.abspath(temp_graph_path)
        optimized_t_table = pd.read_csv(temp_graph_path)
        return optimized_t_table

    def shutdown(self, optimized_t_table: pd.DataFrame):
        pass
