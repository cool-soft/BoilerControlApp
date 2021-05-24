import logging
from typing import Optional

from boiler.temp_graph.io.abstract_async_temp_graph_loader import AbstractAsyncTempGraphLoader
from boiler.temp_graph.io.abstract_sync_temp_graph_dumper import AbstractSyncTempGraphDumper

from backend.services.temp_graph_update_service.temp_graph_update_service import TempGraphUpdateService


class SimpleTempGraphUpdateService(TempGraphUpdateService):

    def __init__(self,
                 temp_graph_loader: Optional[AbstractAsyncTempGraphLoader],
                 temp_graph_dumper: Optional[AbstractSyncTempGraphDumper]
                 ) -> None:

        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance")

        self._temp_graph_loader = temp_graph_loader
        self._temp_graph_dumper = temp_graph_dumper

    async def update_temp_graph_async(self) -> None:
        self._logger.debug("Requested temp graph update")
        temp_graph = await self._temp_graph_loader.load_temp_graph()
        self._temp_graph_dumper.dump_temp_graph(temp_graph)
        self._logger.debug("temp graph is updated")
