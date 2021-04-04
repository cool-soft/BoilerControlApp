import logging

import pandas as pd

from boiler.constants import column_names


class ControlActionsSimpleRepository:

    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of service")

        # TODO: вынести создание пустого DataFrame с заданными колонками куда-нибудь
        self._cache = pd.DataFrame(
            columns=(column_names.TIMESTAMP, column_names.FORWARD_PIPE_COOLANT_TEMP)
        )

    async def get_control_action(self, start_datetime: pd.Timestamp = None, end_datetime: pd.Timestamp = None):
        self._logger.debug(f"Requested boiler control action from {start_datetime} to {end_datetime}")

        control_df = self._cache.copy()
        if start_datetime is not None:
            control_df = control_df[control_df[column_names.TIMESTAMP] >= start_datetime]
        if end_datetime is not None:
            control_df = control_df[control_df[column_names.TIMESTAMP] <= end_datetime]

        return control_df

    async def set_control_action(self, boiler_control_df: pd.DataFrame):
        self._logger.debug("Boiler control action is stored")
        self._cache = boiler_control_df.copy()

    async def update_control_action(self, boiler_control_df: pd.DataFrame):
        self._logger.debug("Stored boiler control action is updated")

        cache_df = self._cache.copy()
        cache_df = cache_df.append(boiler_control_df)
        cache_df = cache_df.drop_duplicates(column_names.TIMESTAMP, keep='last')
        cache_df = cache_df.sort_values(column_names.TIMESTAMP, ignore_index=True)
        self._cache = cache_df

    async def delete_control_action_older_than(self, datetime: pd.Timestamp):
        self._logger.debug(f"Requested deleting boiler contreol data older than {datetime}")

        self._cache = self._cache[self._cache[column_names.TIMESTAMP] >= datetime].copy()
