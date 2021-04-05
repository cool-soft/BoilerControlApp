import logging
from typing import List

import pandas as pd
from dateutil.tz import tzlocal


class UpdatableItem:

    def __init__(self,
                 update_interval: pd.Timedelta = None,
                 dependency: List = None):

        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance")

        if dependency is None:
            dependency = []
        self._dependencyes = dependency
        self._update_interval = update_interval

        self._last_update = None

        self._logger.debug(f"Dependency count {len(self._dependencyes)}")
        self._logger.debug(f"Update interval {self._update_interval}")

    def set_dependency(self, dependency: List):
        self._logger.debug(f"Dependency is set; count {len(self._dependencyes)}")
        self._dependencyes = dependency

    def set_update_interval(self, update_interval: pd.Timedelta):
        self._logger.debug(f"Update interval is set to {update_interval}")
        self._update_interval = update_interval

    def get_next_update(self):
        self._logger.debug("Next update is requested")

        next_update = None
        if self._update_interval is not None:
            if self._last_update is None:
                next_update = pd.Timedelta(seconds=0)
            else:
                datetime_now = pd.Timestamp.now(tz=tzlocal())
                next_update = self._last_update + self._update_interval - datetime_now

        self._logger.debug(f"Next update is {next_update}")
        return next_update

    def get_dependency(self):
        self._logger.debug("Dependency list is requested")

        dependencyes = self._dependencyes.copy()
        self._logger.debug(f"Dependency count: {len(dependencyes)}")

        return dependencyes

    def is_dependendent_on(self, item):
        self._logger.debug(f"Check dependency {item}")

        dependency = False
        if item in self._dependencyes:
            dependency = True
        else:
            for sub_dependency in self._dependencyes:
                if sub_dependency.is_dependent_on(item):
                    dependency = True
                    break

        self._logger.debug(f"Dependency status {dependency} for {item}")
        return dependency

    async def update_async(self):
        await self._run_async_update()
        self._set_last_update_to_now()

    async def _run_async_update(self):
        pass

    def _set_last_update_to_now(self):
        self._last_update = pd.Timestamp.now(tz=tzlocal())
        self._logger.debug(f"Last update is set to {self._last_update}")
