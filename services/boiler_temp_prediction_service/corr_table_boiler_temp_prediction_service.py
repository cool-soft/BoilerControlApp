import logging

import pandas as pd

import constants.column_names
from constants import time_tick
from services.boiler_temp_prediction_service.boiler_temp_prediction_service \
    import BoilerTempPredictionService
from boiler_temp_predictors.corr_table_temp_predictor import CorrTableTempPredictor
from services.temp_requirements_service.temp_requirements_service import TempRequirementsService


class CorrTableBoilerTempPredictionService(BoilerTempPredictionService):

    def __init__(self,
                 temp_predictor: CorrTableTempPredictor = None,
                 temp_requirements_service: TempRequirementsService = None):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of the service")

        self._temp_predictor = temp_predictor
        self._temp_requirements_service = temp_requirements_service

    def set_temp_requirements_service(self, temp_requirements_service):
        self._logger.debug("Set temp requirements service")
        self._temp_requirements_service = temp_requirements_service

    def set_temp_predictor(self, temp_predictor: CorrTableTempPredictor):
        logging.debug("Set temp predictor")
        self._temp_predictor = temp_predictor

    def get_need_boiler_temp(self, start_datetime: pd.Timestamp, end_datetime: pd.Timestamp):
        self._logger.debug(f"Requested predicted boiler t from {start_datetime} to {end_datetime}")

        homes_time_deltas = self._temp_predictor.get_homes_time_deltas()
        max_home_time_delta = homes_time_deltas[constants.column_names.TIME_DELTA].max()
        temp_requirements_end_datetime = end_datetime + (max_home_time_delta * time_tick.TIME_TICK)

        temp_requirements_df = self._temp_requirements_service.get_required_temp(
            start_datetime, temp_requirements_end_datetime
        )

        need_boiler_temp_df = self._temp_predictor.predict_on_temp_requirements(temp_requirements_df)

        return need_boiler_temp_df
