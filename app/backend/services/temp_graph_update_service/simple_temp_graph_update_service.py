import asyncio
import logging
from typing import Optional

from backend.services.temp_graph_update_service.temp_graph_update_service import TempGraphUpdateService
from boiler.temp_graph.io.async_.async_temp_graph_loader import AsyncTempGraphLoader
from boiler.temp_graph.io.sync.sync_temp_graph_dumper import SyncTempGraphDumper


class SimpleTempGraphUpdateService(TempGraphUpdateService):

    def __init__(self,
                 temp_graph_loader: Optional[AsyncTempGraphLoader] = None,
                 temp_graph_dumper: Optional[SyncTempGraphDumper] = None) -> None:

        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance")

        self._service_lock = asyncio.Lock()

        self._temp_graph_loader = temp_graph_loader
        self._temp_graph_dumper = temp_graph_dumper

    def set_temp_graph_loader(self,
                              temp_graph_loader: AsyncTempGraphLoader) -> None:
        self._logger.debug("Temp graph src repository is set")
        self._temp_graph_loader = temp_graph_loader

    def set_temp_graph_dumper(self, temp_graph_dumper: SyncTempGraphDumper) -> None:
        self._logger.debug("Temp graph src repository is set")
        self._temp_graph_dumper = temp_graph_dumper

    async def update_temp_graph_async(self):
        self._logger.debug("Requested temp graph update")
        async with self._service_lock:
            temp_graph = await self._temp_graph_loader.load_temp_graph()
            self._temp_graph_dumper.dump_temp_graph(temp_graph)
            self._logger.debug("temp graph is updated")
