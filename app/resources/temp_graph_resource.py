import os

import pandas as pd
from dependency_injector import resources


class TempGraphResource(resources.Resource):

    def init(self, temp_graph_path) -> pd.DataFrame:
        temp_graph_path = os.path.abspath(temp_graph_path)
        temp_graph = pd.read_csv(temp_graph_path)
        return temp_graph

    def shutdown(self, temp_graph: pd.DataFrame):
        pass
