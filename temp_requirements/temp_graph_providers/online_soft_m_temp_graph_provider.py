import logging
from datetime import datetime

import pandas as pd
import requests
from dateutil.tz import tzlocal

from temp_requirements.temp_graph_parsers.temp_graph_parser import TempGraphParser
from .temp_graph_provider import TempGraphProvider


class OnlineSoftMTempGraphProvider(TempGraphProvider):

    def __init__(self,
                 server_address="https://lysva.agt.town/",
                 update_interval=24 * 3600,
                 temp_graph_parser: TempGraphParser = None):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of the service")

        self._temp_graph_server_address = server_address
        self._temp_graph_parser = temp_graph_parser

        self._temp_graph_update_interval = update_interval
        self._temp_graph_last_update = None
        self._temp_graph_cache = pd.DataFrame()

    def set_server_address(self, server_address):
        self._logger.debug(f"Server address is set to {server_address}")
        self._temp_graph_server_address = server_address

    def set_update_interval(self, update_interval):
        self._logger.debug(f"Temp graph update interval is set to {update_interval}")
        self._temp_graph_update_interval = update_interval

    def set_temp_graph_parser(self, temp_graph_parser: TempGraphParser):
        self._logger.debug("Temp graph parser is set")
        self._temp_graph_parser = temp_graph_parser

    def get_temp_graph(self):
        self._logger.debug(f"Requested temp graph")
        if self._is_cached_temp_graph_expired():
            self._update_temp_graph_from_server()
        return self._temp_graph_cache.copy()

    def _is_cached_temp_graph_expired(self):
        self._logger.debug("Checking that cached temp graph is not expired")

        if self._temp_graph_last_update is None:
            self._logger.debug("Temp graph is never updated")
            return True

        datetime_now = datetime.now(tzlocal())
        temp_graph_lifetime = (datetime_now - self._temp_graph_last_update)
        if temp_graph_lifetime.total_seconds() > self._temp_graph_update_interval:
            self._logger.debug("Cached temp graph is expired")
            return True

        self._logger.debug("Cached temp graph is not expired")
        return False

    def _update_temp_graph_from_server(self):
        self._logger.debug("Updating temp graph from server")
        data = self._get_temp_graph_from_server()
        self._temp_graph_cache = self._temp_graph_parser.parse_temp_graph(data)
        self._temp_graph_last_update = datetime.now(tzlocal())

    def _get_temp_graph_from_server(self):
        self._logger.debug(f"Requesting temp graph from server {self._temp_graph_server_address}")
        url = f"{self._temp_graph_server_address}/JSON/"
        params = {
            "method": "getTempGraphic"
        }
        response = requests.get(url, params=params)
        self._logger.debug(f"Temp graph is loaded from server. Response status code is {response.status_code}")
        return response.text
