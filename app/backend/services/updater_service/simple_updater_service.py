import logging
import asyncio

import pandas as pd
from dateutil.tz import tzlocal

from backend.services.control_action_prediction_service.control_action_prediction_service import \
    ControlActionPredictionService
from backend.services.temp_graph_update_service.temp_graph_update_service import TempGraphUpdateService
from backend.services.temp_requirements_service.temp_requirements_service import TempRequirementsService
from backend.services.updater_service.updater_service import UpdaterService


class SimpleUpdaterService(UpdaterService):

    def __init__(self,
                 control_action_predictor_factory=None,
                 temp_graph_updater_factory=None,
                 temp_requirements_calculator_factory=None,
                 temp_graph_update_interval=86400,
                 control_action_update_interval=600):

        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of the service")

        self._control_action_predictor_factory = control_action_predictor_factory
        self._temp_graph_updater_factory = temp_graph_updater_factory
        self._temp_requirements_calculator_factory = temp_requirements_calculator_factory

        self._temp_graph_update_interval = temp_graph_update_interval
        self._control_action_update_interval = control_action_update_interval

        self._temp_graph_last_update = None
        self._control_action_last_update = None

        self._async_update_lock = asyncio.Lock()

    def set_control_action_predictor_factory(self, factory):
        self._logger.debug("Control action predictor factory is set")
        self._control_action_predictor_factory = factory

    def set_temp_graph_updater_factory(self, factory):
        self._logger.debug("Temp graph updater factory is set")
        self._temp_graph_updater_factory = factory

    def set_temp_requirements_calculator_factory(self, factory):
        self._logger.debug("Temp requirements calculator factory is set")
        self._temp_requirements_calculator_factory = factory

    def set_temp_graph_update_interval(self, update_interval):
        self._logger.debug(f"Temp graph update interval is set to {update_interval}")
        self._temp_graph_update_interval = update_interval

    def set_control_action_update_interval(self, update_interval):
        self._logger.debug(f"Control action update interval is set to {update_interval}")
        self._control_action_update_interval = update_interval

    async def run_async(self):
        while True:
            temp_graph_next_update = self._get_temp_graph_next_update()
            control_action_next_update = self._get_control_action_next_update()
            sleep_time = min(temp_graph_next_update, control_action_next_update)
            sleep_time = max(sleep_time, 0)
            await asyncio.sleep(sleep_time)
            await self.run_async_one_cycle()

    async def run_async_one_cycle(self, force=False):
        async with self._async_update_lock:
            if force or self._get_control_action_next_update() <= 0:
                self._update_control_action()
            if force or self._get_temp_graph_next_update() <= 0:
                self._update_temp_graph()

    def _get_control_action_next_update(self):
        next_update = self._get_next_update(self._control_action_last_update,
                                            self._control_action_update_interval)
        return next_update

    def _get_temp_graph_next_update(self):
        next_update = self._get_next_update(self._temp_graph_last_update,
                                            self._temp_graph_update_interval)
        return next_update

    # noinspection PyMethodMayBeStatic
    def _get_next_update(self, last_update, update_interval):
        next_update = 0
        if last_update is not None:
            time_now = pd.Timestamp.now(tz=tzlocal())
            lifetime = (time_now - last_update).total_seconds()
            next_update = update_interval - lifetime
        return next_update

    def _update_control_action(self):
        temp_requirements_calculator: TempRequirementsService = self._temp_requirements_calculator_factory()
        temp_requirements_calculator.update_temp_requirements()
        control_action_predictor: ControlActionPredictionService = self._control_action_predictor_factory()
        control_action_predictor.update_control_actions()
        self._control_action_last_update = pd.Timestamp.now(tz=tzlocal())

    def _update_temp_graph(self):
        temp_graph_updater: TempGraphUpdateService = self._temp_graph_updater_factory()
        temp_graph_updater.update_temp_graph()
        self._temp_graph_last_update = pd.Timestamp.now(tz=tzlocal())
