import asyncio
import logging

import pandas as pd
from dateutil.tz import tzlocal

from boiler.temp_graph.repository.online_soft_m_temp_graph_repository import TempGraphProvider
from backend.services.temp_graph_service.temp_graph_service import TempGraphService


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
        self._temp_graph_cache_lock = asyncio.Lock()

    def set_temp_graph_provider(self, temp_graph_provider: TempGraphProvider):
        self._temp_graph_provider = temp_graph_provider

    def set_update_interval(self, update_interval):
        self._logger.debug(f"Temp graph update interval is set to {update_interval}")
        self._temp_graph_update_interval = update_interval

    async def get_temp_graph(self) -> pd.DataFrame:
        async with self._temp_graph_cache_lock:
            self._logger.debug(f"Requested temp graph")
            if self._is_cached_temp_graph_expired():
                self._update_temp_graph()
            temp_graph = self._temp_graph_cache.copy()

        return temp_graph

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
