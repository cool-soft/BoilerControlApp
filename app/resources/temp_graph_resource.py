import logging
import os

from dependency_injector import resources
import pandas as pd


class TempGraphResource(resources.Resource):

    def init(self, temp_graph_path) -> pd.DataFrame:
        logger = logging.getLogger(self.__class__.__name__)
        temp_graph_path = os.path.abspath(temp_graph_path)
        logger.debug(f"Loading temp graph from {temp_graph_path}")
        temp_graph = pd.read_csv(temp_graph_path)
        return temp_graph

    def shutdown(self, temp_graph: pd.DataFrame):
        pass
