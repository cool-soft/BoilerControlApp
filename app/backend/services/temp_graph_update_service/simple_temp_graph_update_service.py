import asyncio
import logging

from backend.services.temp_graph_update_service.temp_graph_update_service import TempGraphUpdateService
from boiler.temp_graph.repository.online_soft_m_temp_graph_repository import TempGraphRepository


class SimpleTempGraphUpdateService(TempGraphUpdateService):

    def __init__(self,
                 temp_graph_src_repository: TempGraphRepository = None,
                 temp_graph_repository: TempGraphRepository = None):

        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of the provider")

        self._service_lock = asyncio.Lock()

        self._temp_graph_src_repository = temp_graph_src_repository
        self._temp_graph_repository = temp_graph_repository

    def set_temp_graph_src_repository(self, temp_graph_src_repository: TempGraphRepository):
        self._logger.debug("Temp graph src repository is set")
        self._temp_graph_src_repository = temp_graph_src_repository

    def set_temp_graph_repository(self, temp_graph_repository: TempGraphRepository):
        self._logger.debug("Temp graph src repository is set")
        self._temp_graph_repository = temp_graph_repository

    async def update_temp_graph_async(self):
        self._logger.debug("Requested temp graph update")

        async with self._service_lock:
            temp_graph = await self._temp_graph_src_repository.get_temp_graph()
            await self._temp_graph_repository.set_temp_graph(temp_graph)

            self._logger.debug("temp graph is updated")
