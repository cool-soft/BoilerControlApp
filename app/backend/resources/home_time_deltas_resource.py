import logging
import os

import pandas as pd
from dependency_injector import resources


class HomeTimeDeltasResource(resources.Resource):

    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of Resource")

    def init(self, homes_deltas_path) -> pd.DataFrame:
        homes_deltas_path = os.path.abspath(homes_deltas_path)
        self._logger.debug(f"Loading home time deltas from {homes_deltas_path}")

        homes_time_deltas = pd.read_csv(homes_deltas_path)

        return homes_time_deltas

    def shutdown(self, homes_time_deltas: pd.DataFrame):
        pass
