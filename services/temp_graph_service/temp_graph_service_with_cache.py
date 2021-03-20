import logging

import pandas as pd
from dateutil.tz import tzlocal

from services.temp_graph_service.temp_graph_service import TempGraphService
from temp_graph.providers.temp_graph_provider import TempGraphProvider


class TempGraphServiceWithCache(TempGraphService):

    def __init__(self,
                 temp_graph_provider: TempGraphProvider = None,
                 update_interval=24 * 3600):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of the service")

        self._temp_graph_provider = temp_graph_provider
        self._temp_graph_update_interval = update_interval
        self._temp_graph_last_update = None
        self._temp_graph_cache = pd.DataFrame()

    def set_temp_graph_provider(self, temp_graph_provider: TempGraphProvider):
        self._temp_graph_provider = temp_graph_provider

    def set_update_interval(self, update_interval):
        self._logger.debug(f"Temp graph update interval is set to {update_interval}")
        self._temp_graph_update_interval = update_interval

    def get_temp_graph(self) -> pd.DataFrame:
        self._logger.debug(f"Requested temp graph")
        if self._is_cached_temp_graph_expired():
            self._update_temp_graph()
        return self._temp_graph_cache.copy()

    def _is_cached_temp_graph_expired(self):
        self._logger.debug("Checking that cached temp graph is not expired")

        if self._temp_graph_last_update is None:
            self._logger.debug("Temp graph is never updated")
            return True

        datetime_now = pd.Timestamp.now(tz=tzlocal())
        temp_graph_lifetime = (datetime_now - self._temp_graph_last_update)
        if temp_graph_lifetime.total_seconds() > self._temp_graph_update_interval:
            self._logger.debug("Cached temp graph is expired")
            return True

        self._logger.debug("Cached temp graph is not expired")
        return False

    def _update_temp_graph(self):
        self._logger.debug("Requesting new temp graph")
        self._temp_graph_cache = self._temp_graph_provider.get_temp_graph()
        self._temp_graph_last_update = pd.Timestamp.now(tz=tzlocal())
