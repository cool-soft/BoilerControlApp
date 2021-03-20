import logging

import requests

from .temp_graph_provider import TempGraphProvider
from ..parsers.temp_graph_parser import TempGraphParser


class OnlineSoftMTempGraphProvider(TempGraphProvider):

    def __init__(self,
                 server_address="https://lysva.agt.town/",
                 temp_graph_parser: TempGraphParser = None):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of the service")

        self._temp_graph_server_address = server_address
        self._temp_graph_parser = temp_graph_parser

    def set_server_address(self, server_address):
        self._logger.debug(f"Server address is set to {server_address}")
        self._temp_graph_server_address = server_address

    def set_temp_graph_parser(self, temp_graph_parser: TempGraphParser):
        self._logger.debug("Temp graph parser is set")
        self._temp_graph_parser = temp_graph_parser

    def get_temp_graph(self):
        self._logger.debug(f"Requested temp graph")
        data = self._get_temp_graph_from_server()
        temp_graph = self._temp_graph_parser.parse_temp_graph(data)
        return temp_graph

    def _get_temp_graph_from_server(self):
        self._logger.debug(f"Requesting temp graph from server {self._temp_graph_server_address}")
        url = f"{self._temp_graph_server_address}/JSON/"
        params = {
            "method": "getTempGraphic"
        }
        response = requests.get(url, params=params)
        self._logger.debug(f"Temp graph is loaded from server. Response status code is {response.status_code}")
        return response.text
