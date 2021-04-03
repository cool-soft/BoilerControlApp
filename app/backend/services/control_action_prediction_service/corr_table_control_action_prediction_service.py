import asyncio
import logging

import pandas as pd
from dateutil.tz import tzlocal

from boiler.constants import column_names, time_tick
from boiler.temp_predictors.corr_table_temp_predictor import CorrTableTempPredictor
from backend.repositories.control_action_cache_repository import ControlActionsCacheRepository
from backend.repositories.temp_requirements_cache_repository import TempRequirementsCacheRepository
from backend.services.control_action_prediction_service.control_action_prediction_service \
    import ControlActionPredictionService


class CorrTableControlActionPredictionService(ControlActionPredictionService):

    def __init__(self,
                 temp_predictor: CorrTableTempPredictor = None,
                 temp_requirements_repository: TempRequirementsCacheRepository = None,
                 control_actions_repository: ControlActionsCacheRepository = None):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of the service")

        self._service_lock = asyncio.Lock()
        self._temp_predictor = temp_predictor
        self._temp_requirements_repository = temp_requirements_repository
        self._control_action_repository = control_actions_repository

    def set_temp_requirements_repository(self, temp_requirements_repository: TempRequirementsCacheRepository):
        self._logger.debug("Set temp requirements repository")
        self._temp_requirements_repository = temp_requirements_repository

    def set_control_actions_repository(self, control_actions_repository: ControlActionsCacheRepository):
        self._logger.debug("Set control actions repository")
        self._control_action_repository = control_actions_repository

    def set_temp_predictor(self, temp_predictor: CorrTableTempPredictor):
        logging.debug("Set temp predictor")
        self._temp_predictor = temp_predictor

    async def update_control_actions(self):
        self._logger.debug(f"Requested updating control actions")

        with self._service_lock:
            start_datetime = pd.Timestamp.now(tz=tzlocal())
            temp_requirements_df = await self._temp_requirements_repository.get_temp_requirements(start_datetime)

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
