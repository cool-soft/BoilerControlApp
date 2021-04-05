import asyncio
import logging

import pandas as pd
from dateutil.tz import tzlocal

from boiler.constants import column_names
from boiler.temp_requirements.repository.temp_requirements_simple_repository import TempRequirementsSimpleRepository
from boiler.temp_predictors.corr_table_temp_predictor import CorrTableTempPredictor
from backend.repositories.control_action_simple_repository import ControlActionsSimpleRepository
from backend.services.control_action_prediction_service.control_actions_prediction_service import \
    ControlActionPredictionService


class CorrTableControlActionPredictionService(ControlActionPredictionService):

    def __init__(self,
                 temp_predictor: CorrTableTempPredictor = None,
                 temp_requirements_repository: TempRequirementsSimpleRepository = None,
                 control_actions_repository: ControlActionsSimpleRepository = None):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of the provider")

        self._service_lock = asyncio.Lock()
        self._temp_predictor = temp_predictor
        self._temp_requirements_repository = temp_requirements_repository
        self._control_action_repository = control_actions_repository

    def set_temp_requirements_repository(self, temp_requirements_repository: TempRequirementsSimpleRepository):
        self._logger.debug("Set temp requirements repository")
        self._temp_requirements_repository = temp_requirements_repository

    def set_control_actions_repository(self, control_actions_repository: ControlActionsSimpleRepository):
        self._logger.debug("Set control actions repository")
        self._control_action_repository = control_actions_repository

    def set_temp_predictor(self, temp_predictor: CorrTableTempPredictor):
        logging.debug("Set temp predictor")
        self._temp_predictor = temp_predictor

    async def predict_control_actions_async(self):
        self._logger.debug("Requested updating control actions")

        async with self._service_lock:
            control_action_df = await self._calc_control_actions()
            await self._control_action_repository.set_control_action(control_action_df)
            await self._drop_expired_control_actions()

    async def _calc_control_actions(self):
        self._logger.debug("Requested calculating control actions")

        start_datetime = pd.Timestamp.now(tz=tzlocal())
        self._logger.debug(f"Requesting temp requirements from {start_datetime}")
        temp_requirements_df: pd.DataFrame = \
            await self._temp_requirements_repository.get_temp_requirements(start_datetime)
        self._logger.debug(f"Gathered {len(temp_requirements_df)} temp requirements")

        self._logger.debug("Prediting control actions on temp reuirements")
        required_temp_arr = temp_requirements_df[column_names.FORWARD_PIPE_COOLANT_TEMP].to_numpy()
        need_temp_list = self._temp_predictor.predict_on_temp_requirements(required_temp_arr)
        control_actions_count = len(need_temp_list)
        self._logger.debug(f"Calculated {control_actions_count} actions")

        temp_requirements_dates_list = temp_requirements_df[column_names.TIMESTAMP].to_list()
        control_actions_dates_list = temp_requirements_dates_list[:control_actions_count]
        control_action_df = pd.DataFrame({
            column_names.TIMESTAMP: control_actions_dates_list,
            column_names.FORWARD_PIPE_COOLANT_TEMP: need_temp_list
        })

        return control_action_df

    async def _drop_expired_control_actions(self):
        datetime_now = pd.Timestamp.now(tz=tzlocal())
        self._logger.debug(f"Droping expiried control actions, that older than {datetime_now}")
        await self._control_action_repository.delete_control_action_older_than(datetime_now)
