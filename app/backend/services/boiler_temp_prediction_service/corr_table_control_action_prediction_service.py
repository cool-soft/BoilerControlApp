import asyncio
import logging

import pandas as pd

from boiler.constants import column_names, time_tick
from boiler.temp_predictors.corr_table_temp_predictor import CorrTableTempPredictor
from backend.repositories.async_control_action_repository import AsyncControlActionsRepository
from backend.repositories.async_temp_requirements_repository import AsyncTempRequirementsRepository
from backend.services.boiler_temp_prediction_service.control_action_prediction_service \
    import ControlActionPredictionService


class CorrTableControlActionPredictionService(ControlActionPredictionService):

    def __init__(self,
                 temp_predictor: CorrTableTempPredictor = None,
                 temp_requirements_repository: AsyncTempRequirementsRepository = None,
                 control_actions_repository: AsyncControlActionsRepository = None):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of the service")

        self._service_lock = asyncio.Lock()
        self._temp_predictor = temp_predictor
        self._temp_requirements_repository = temp_requirements_repository
        self._control_action_repository = control_actions_repository

    def set_temp_requirements_repository(self, temp_requirements_repository: AsyncTempRequirementsRepository):
        self._logger.debug("Set temp requirements repository")
        self._temp_requirements_repository = temp_requirements_repository

    def set_control_actions_repository(self, control_actions_repository: AsyncControlActionsRepository):
        self._logger.debug("Set control actions repository")
        self._control_action_repository = control_actions_repository

    def set_temp_predictor(self, temp_predictor: CorrTableTempPredictor):
        logging.debug("Set temp predictor")
        self._temp_predictor = temp_predictor

    async def update_control_actions(self, start_datetime: pd.Timestamp, end_datetime: pd.Timestamp):
        self._logger.debug(f"Requested updating control actions from {start_datetime} to {end_datetime}")

        with self._service_lock:
            temp_requirements_end_datetime = self._calc_temp_requirements_end_datetime(end_datetime)
            temp_requirements_df = await self._temp_requirements_repository.get_temp_requirements(
                start_datetime, temp_requirements_end_datetime
            )

            required_temp_arr = temp_requirements_df[column_names.FORWARD_PIPE_COOLANT_TEMP].to_numpy()
            need_temp_list = self._temp_predictor.predict_on_temp_requirements(required_temp_arr)
            boiler_temp_count = len(need_temp_list)
            temp_requirements_dates_list = temp_requirements_df[column_names.TIMESTAMP].to_list()
            control_actions_dates_list = temp_requirements_dates_list[:boiler_temp_count]

            control_action_df = pd.DataFrame({
                column_names.TIMESTAMP: control_actions_dates_list,
                column_names.FORWARD_PIPE_COOLANT_TEMP: need_temp_list
            })
            await self._control_action_repository.set_control_action(control_action_df)

    def _calc_temp_requirements_end_datetime(self, end_datetime):
        homes_time_deltas = self._temp_predictor.get_homes_time_deltas()
        max_home_time_delta = homes_time_deltas[column_names.TIME_DELTA].max()
        temp_requirements_end_datetime = end_datetime + (max_home_time_delta * time_tick.TIME_TICK)
        return temp_requirements_end_datetime
