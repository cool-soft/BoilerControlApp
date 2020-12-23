import logging
from datetime import datetime

import pandas as pd
import requests
from dateutil.tz import tzlocal

from dataset_utils import data_consts
from dataset_utils.preprocess_utils import rename_column
from .temp_graph_service import TempGraphService


class OnlineTempGraphService(TempGraphService):

    def __init__(self, server_address=None, update_interval=24*3600):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of the service")
        self._temp_graph_server_address = server_address
        self._temp_graph_last_update = None
        self._temp_graph_update_interval = update_interval
        self._temp_graph_cache = pd.DataFrame()

    def set_server_address(self, server_address):
        self._logger.debug(f"Server address is set to {server_address}")
        self._temp_graph_server_address = server_address

    def set_update_interval(self, update_interval):
        self._logger.debug(f"Temp graph update interval is set to {update_interval}")
        self._temp_graph_update_interval = update_interval

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
        new_temp_graph_df = self._preprocess_temp_graph(data)
        self._temp_graph_cache = new_temp_graph_df
        self._temp_graph_last_update = datetime.now(tzlocal())

    # noinspection PyMethodMayBeStatic
    def _get_temp_graph_from_server(self):
        self._logger.debug(f"Requesting temp graph from server {self._temp_graph_server_address}")
        url = f"{self._temp_graph_server_address}/JSON/"
        # noinspection SpellCheckingInspection
        params = {
            "method": "getTempGraphic"
        }
        response = requests.get(url, params=params)
        self._logger.debug(f"Temp graph is loaded. Response status code is {response.status_code}")
        return response.text

    # noinspection PyMethodMayBeStatic
    def _preprocess_temp_graph(self, response_text):
        self._logger.debug("Preprocessing temp graph")
        df = pd.read_json(response_text)
        df = rename_column(df, data_consts.SOFT_M_TEMP_GRAPH_WEATHER_COLUMN_NAME, data_consts.WEATHER_T_COLUMN_NAME)
        df = rename_column(df,
                           data_consts.SOFT_M_TEMP_GRAPH_REQUIRED_T_AT_HOME_IN_COLUMN_NAME,
                           data_consts.REQUIRED_T_AT_HOME_IN_COLUMN_NAME)
        df = rename_column(df,
                           data_consts.SOFT_M_TEMP_GRAPH_REQUIRED_T_AT_HOME_OUT_COLUMN_NAME,
                           data_consts.REQUIRED_T_AT_HOME_OUT_COLUMN_NAME)
        return df
