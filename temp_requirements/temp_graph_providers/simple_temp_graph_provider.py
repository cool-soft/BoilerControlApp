import logging

from .temp_graph_provider import TempGraphProvider


class SimpleTempGraphProvider(TempGraphProvider):

    def __init__(self, temp_graph=None):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of the service")
        self._temp_graph = temp_graph

    def set_temp_graph(self, temp_graph):
        self._logger.debug("Temp graph is set")
        self._temp_graph = temp_graph

    def get_temp_graph(self):
        self._logger.debug("Requested temp graph")
        return self._temp_graph.copy()
