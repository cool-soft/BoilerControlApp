import logging
from typing import List, Optional, Union

import pandas as pd
from dateutil.tz import tzlocal


class UpdatableItem:

    def __init__(self,
                 update_interval: Optional[pd.Timedelta] = None,
                 dependencies: Optional[List[__qualname__]] = None):

        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance")

        if dependencies is None:
            dependencies = []
        self._dependencies = dependencies
        self._update_interval = update_interval

        self._logger.debug(f"Dependency count {len(self._dependencies)}")
        self._logger.debug(f"Update interval {self._update_interval}")

        self._last_update_datetime = None

    def set_dependencies(self, dependencies: List[__qualname__]):
        self._logger.debug(f"Dependencies is set; count {len(self._dependencies)}")

        self._dependencies = dependencies

    def set_update_interval(self, update_interval: Union[pd.Timedelta, None]):
        self._logger.debug(f"Update interval is set to {update_interval}")

        self._update_interval = update_interval

    def get_dependencies(self) -> List[__qualname__]:
        self._logger.debug("Dependency list is requested")

        dependencies = self._dependencies.copy()
        self._logger.debug(f"Dependency count: {len(dependencies)}")
        return dependencies

    def get_next_update_datetime(self) -> Optional[pd.Timedelta]:
        self._logger.debug("Requested next update datetime")

        next_update_datetime = None
        if self._update_interval is not None:
            if self._last_update_datetime is None:
                next_update_datetime = pd.Timestamp.now(tz=tzlocal())
            else:
                next_update_datetime = self._last_update_datetime + self._update_interval

        self._logger.debug(f"Next update datetime is {next_update_datetime}")
        return next_update_datetime

    def get_last_updated_datetime(self) -> Optional[pd.Timedelta]:
        self._logger.debug("Last update datetime is requested")

        self._logger.debug(f"Last update datetime is {self._last_update_datetime}")
        return self._last_update_datetime

    def is_need_update(self):
        self._logger.debug("Check that item need update")

        need_update = False
        if self._last_update_datetime is None:
            need_update = True
        elif self._is_dependencies_newer_updated():
            need_update = True
        elif self.get_next_update_datetime() <= pd.Timestamp.now(tz=tzlocal()):
            need_update = True

        self._logger.debug(f"Need upate status is {need_update}")
        return need_update

    def _is_dependencies_newer_updated(self) -> bool:
        self._logger.debug("Check that dependencies are newer updated")

        dependency_newer_updated = False
        for dependency in self._dependencies:
            dependency_last_update_datetime = dependency.get_last_update_datetime()
            if dependency_last_update_datetime is None:
                raise ValueError(f"Dependent item should not be updated before the dependency;"
                                 f"Dependency that need update is {dependency.__class__.__name__}")

            if self._last_update_datetime <= dependency_last_update_datetime:
                dependency_newer_updated = True
                break

        self._logger.debug(f"Dependencies update status is {dependency_newer_updated}")
        return dependency_newer_updated

    async def update_async(self):
        await self._run_update_async()
        self._set_last_update_datetime_to_now()

    async def _run_update_async(self):
        pass

    def _set_last_update_datetime_to_now(self):
        last_update_datetime = pd.Timestamp.now(tz=tzlocal())
        self._logger.debug(f"Last update is set to {last_update_datetime}")
        self._last_update_datetime = last_update_datetime
