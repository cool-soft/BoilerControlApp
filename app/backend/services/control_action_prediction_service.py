from datetime import timedelta
from typing import Tuple

import pandas as pd
from boiler.control_action.predictors.abstract_control_action_predictor import AbstractControlActionPredictor
from boiler.data_processing.timestamp_round_algorithm import AbstractTimestampRoundAlgorithm
from boiler.heating_system.model_parameters.abstract_model_requirements import AbstractModelParameters
from dateutil import tz
from sqlalchemy.orm import scoped_session

from backend.providers.temp_requirements_provider import TempRequirementsProvider
from backend.repositories.control_action_repository import ControlActionRepository


class ControlActionPredictionService:

    def __init__(self,
                 model_parameters: AbstractModelParameters,
                 temp_requirements_provider: TempRequirementsProvider,
                 control_action_predictor: AbstractControlActionPredictor,
                 db_session_factory: scoped_session,
                 control_action_repository: ControlActionRepository,
                 timestamp_round_algo: AbstractTimestampRoundAlgorithm,
                 time_tick: pd.Timedelta,
                 timedelta_predict_forward: timedelta = timedelta(seconds=3600),
                 ) -> None:
        self._model_parameters = model_parameters
        self._temp_requirements_provider = temp_requirements_provider
        self._control_action_predictor = control_action_predictor
        self._session_factory = db_session_factory
        self._control_action_repository = control_action_repository
        self._timestamp_round_algo = timestamp_round_algo
        self._time_tick = time_tick
        self._timedelta_predict_forward = timedelta_predict_forward

    def update_control_actions(self) -> None:
        control_action_df = self._calc_control_action_()
        with self._session_factory() as session:
            self._control_action_repository.add_control_action(control_action_df)
            session.commit()
        self._session_factory.remove()

    def _calc_control_action_(self):
        control_action_start_timestamp, control_action_end_timestamp = self._calc_control_action_start_end_timestamps()
        requirements_start_timestamp, requirements_end_timestamp = self._calc_temp_requirements_start_end_timestamp(
            control_action_start_timestamp,
            control_action_end_timestamp
        )
        temp_requirements_df = self._temp_requirements_provider.get_temp_requirements(
            requirements_start_timestamp, requirements_end_timestamp
        )
        control_action_df = self._calc_control_action_on_temp_requirements(
            control_action_start_timestamp,
            control_action_end_timestamp,
            temp_requirements_df
        )
        return control_action_df

    def _calc_control_action_start_end_timestamps(self):
        control_action_start_timestamp = pd.Timestamp.now(tz=tz.UTC)
        control_action_start_timestamp = self._timestamp_round_algo.round_value(control_action_start_timestamp)
        control_action_end_timestamp = control_action_start_timestamp + self._timedelta_predict_forward
        return control_action_start_timestamp, control_action_end_timestamp

    def _calc_temp_requirements_start_end_timestamp(self,
                                                    control_action_start_timestamp: pd.Timestamp,
                                                    control_action_end_timestamp: pd.Timestamp
                                                    ) -> Tuple[pd.Timestamp, pd.Timestamp]:
        temp_requirements_start_timestamp = \
            control_action_start_timestamp + self._model_parameters.get_min_heating_system_lag()
        temp_requirements_end_timestamp = \
            control_action_end_timestamp + self._model_parameters.get_max_heating_system_lag() + self._time_tick
        return temp_requirements_start_timestamp, temp_requirements_end_timestamp

    def _calc_control_action_on_temp_requirements(self,
                                                  control_action_start_timestamp,
                                                  control_action_end_timestamp,
                                                  temp_requirements_df) -> pd.DataFrame:
        control_actions_list = []
        control_action_timestamp = control_action_start_timestamp
        while control_action_timestamp <= control_action_end_timestamp:
            control_action_df = self._control_action_predictor.predict_one(
                temp_requirements_df,
                control_action_timestamp
            )
            control_actions_list.append(control_action_df)
            control_action_timestamp += self._time_tick
        control_action_df = pd.concat(control_actions_list)
        return control_action_df
