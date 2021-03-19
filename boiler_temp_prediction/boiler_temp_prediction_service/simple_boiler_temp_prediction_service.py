import logging

import numpy as np
import pandas as pd

import heating_system.temp_requirements_utils.constants.column_names
from heating_system import column_names, time_tick
from .boiler_temp_prediction_service import BoilerTempPredictionService


class SimpleBoilerTempPredictionService(BoilerTempPredictionService):

    def __init__(self,
                 temp_correlation_table=None,
                 home_time_deltas=None,
                 temp_requirements_service=None,
                 home_min_temp_coefficient=1):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of the service")

        self._temp_correlation_table = temp_correlation_table
        self._homes_time_deltas = home_time_deltas
        self._temp_requirements_service = temp_requirements_service
        self._home_min_temp_coefficient = home_min_temp_coefficient

    def set_homes_time_deltas(self, homes_time_deltas):
        self._logger.debug("Set homes time deltas")
        self._homes_time_deltas = homes_time_deltas

    def set_temp_correlation_table(self, temp_correlation_table):
        self._logger.debug("Set temp correlation table")
        self._temp_correlation_table = temp_correlation_table

    def set_temp_requirements_service(self, temp_requirements_service):
        self._logger.debug("Set temp requirements service")
        self._temp_requirements_service = temp_requirements_service

    def set_home_min_temp_coefficient(self, min_temp_coefficient):
        logging.debug(f"Set home min temp coefficient to {min_temp_coefficient}")
        self._home_min_temp_coefficient = min_temp_coefficient

    def get_need_boiler_temp(self, start_datetime, end_datetime):
        self._logger.debug(f"Requested predicted boiler t from {start_datetime} to {end_datetime}")

        max_home_time_delta = self._homes_time_deltas[column_names.TIME_DELTA].max()
        temp_requirements_end_datetime = end_datetime + (max_home_time_delta * time_tick.TIME_TICK)

        temp_requirements_df = self._temp_requirements_service.get_required_temp(
            start_datetime, temp_requirements_end_datetime
        )
        if len(temp_requirements_df) < max_home_time_delta + 1:
            return pd.DataFrame({
                column_names.TIMESTAMP: [],
                column_names.BOILER_OUT_TEMP: []
            })

        need_boiler_temp_df = self._get_need_boiler_temp_for_temp_requirements_df(temp_requirements_df)

        return need_boiler_temp_df

    def _get_need_boiler_temp_for_temp_requirements_df(self, temp_requirements_df):
        self._logger.debug(f"Requested need boiler temp for temp requirements")

        max_home_time_delta = self._homes_time_deltas[column_names.TIME_DELTA].max()
        need_boiler_temp_df_len = len(temp_requirements_df) - max_home_time_delta

        temp_requirements_arr = temp_requirements_df[
            heating_system.temp_requirements_utils.constants.column_names.FORWARD_PIPE_TEMP].to_numpy()
        need_boiler_temp_arr = np.empty(shape=(need_boiler_temp_df_len,), dtype=np.float)
        for time_moment_number in range(need_boiler_temp_df_len):
            need_boiler_temp = self._calc_need_boiler_temp_for_time_moment(time_moment_number, temp_requirements_arr)
            need_boiler_temp_arr[time_moment_number] = need_boiler_temp

        temp_requirements_dates_list = temp_requirements_df[column_names.TIMESTAMP].to_list()
        need_boiler_temp_dates_list = temp_requirements_dates_list[:need_boiler_temp_df_len]
        need_boiler_temp_df = pd.DataFrame({
            column_names.TIMESTAMP: need_boiler_temp_dates_list,
            column_names.BOILER_OUT_TEMP: need_boiler_temp_arr
        })
        return need_boiler_temp_df

    def _calc_need_boiler_temp_for_time_moment(self, time_moment_number, temp_requirements_arr):
        need_boiler_temp = float("-inf")

        home_names_list = self._homes_time_deltas[column_names.HOME_NAME].to_list()
        time_deltas_list = self._homes_time_deltas[column_names.TIME_DELTA].to_list()
        for home_name, home_time_delta in zip(home_names_list, time_deltas_list):
            need_home_temp = temp_requirements_arr[time_moment_number + home_time_delta]
            need_home_temp *= self._home_min_temp_coefficient
            need_temp_condition = self._temp_correlation_table[home_name] >= need_home_temp
            need_boiler_temp_for_home = self._temp_correlation_table[
                need_temp_condition][column_names.BOILER_OUT_TEMP].min()
            need_boiler_temp = max(need_boiler_temp, need_boiler_temp_for_home)

        return need_boiler_temp
