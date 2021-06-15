from boiler.temp_graph.io.abstract_async_temp_graph_loader import AbstractAsyncTempGraphLoader
from boiler.temp_graph.io.abstract_sync_temp_graph_dumper import AbstractSyncTempGraphDumper

from backend.logger import logger
from backend.services.temp_graph_update_service.temp_graph_update_service import TempGraphUpdateService


class SimpleTempGraphUpdateService(TempGraphUpdateService):

    def __init__(self,
                 temp_graph_loader: AbstractAsyncTempGraphLoader,
                 temp_graph_dumper: AbstractSyncTempGraphDumper
                 ) -> None:
        self._temp_graph_loader = temp_graph_loader
        self._temp_graph_dumper = temp_graph_dumper

        logger.debug("Creating instance")

    async def update_temp_graph_async(self) -> None:
        logger.debug("Requested temp graph update")
        temp_graph = await self._temp_graph_loader.load_temp_graph()
        self._temp_graph_dumper.dump_temp_graph(temp_graph)
        logger.debug("temp graph is updated")
