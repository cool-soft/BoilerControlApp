from boiler.temp_graph.io.abstract_sync_temp_graph_dumper import AbstractSyncTempGraphDumper
from boiler.temp_graph.io.abstract_sync_temp_graph_loader import AbstractSyncTempGraphLoader

from backend.logging import logger


class SimpleTempGraphUpdateService:

    def __init__(self,
                 temp_graph_loader: AbstractSyncTempGraphLoader,
                 temp_graph_dumper: AbstractSyncTempGraphDumper
                 ) -> None:
        self._temp_graph_loader = temp_graph_loader
        self._temp_graph_dumper = temp_graph_dumper

        logger.debug("Creating instance")

    def update_temp_graph(self) -> None:
        logger.info("Requesting temp graph update")
        temp_graph = self._temp_graph_loader.load_temp_graph()
        self._temp_graph_dumper.dump_temp_graph(temp_graph)
        logger.debug("temp graph is updated")
