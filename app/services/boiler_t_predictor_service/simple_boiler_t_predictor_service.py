import logging

import numpy as np
import pandas as pd

import column_names
import time_tick
from .boiler_t_predictor_service import BoilerTPredictorService


class SimpleBoilerTPredictorService(BoilerTPredictorService):

    def __init__(self,
                 optimized_t_table=None,
                 home_time_deltas=None,
                 temp_requirements_service=None,
                 home_t_dispersion_coefficient=1):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of the service")
        self._optimized_t_table = optimized_t_table
        self._homes_time_deltas = home_time_deltas
        self._temp_requirements_service = temp_requirements_service
        self._home_t_dispersion_coefficient = home_t_dispersion_coefficient

    def set_homes_time_deltas(self, homes_time_deltas):
        self._logger.debug("Set homes time deltas")
        self._homes_time_deltas = homes_time_deltas

    def set_optimized_t_table(self, t_table):
        self._logger.debug("Set optimized t table")
        self._optimized_t_table = t_table

    def set_temp_requirements_service(self, temp_graph_service):
        self._logger.debug("Set temp requirements service")
        self._temp_requirements_service = temp_graph_service

    def set_dispersion_coefficient(self, coefficient):
        logging.debug(f"Set dispersion coefficient to {coefficient}")
        self._home_t_dispersion_coefficient = coefficient

    def get_need_boiler_t(self, start_datetime, end_datetime):
        self._logger.debug(f"Requested predicted boiler t "
                           f"from {start_datetime} to {end_datetime}")

        max_home_time_delta = self._homes_time_deltas[column_names.TIME_DELTA].max()
        temp_requirements_end_datetime = end_datetime + (
                max_home_time_delta * time_tick.TIME_TICK
        )

        temp_requirements_df = self._temp_requirements_service.get_required_temp(
            start_datetime, temp_requirements_end_datetime
        )
        if len(temp_requirements_df) < max_home_time_delta + 1:
            return pd.DataFrame({
                column_names.TIMESTAMP: [],
                column_names.BOILER: []
            })

        need_boiler_t_df = self._get_need_boiler_t(temp_requirements_df)

        return need_boiler_t_df

    def _get_need_boiler_t(self, temp_requirements_df):
        self._logger.debug(f"Requested need boiler temp for temp requirements")

        max_home_time_delta = self._homes_time_deltas[column_names.TIME_DELTA].max()
        need_boiler_t_df_len = len(temp_requirements_df) - max_home_time_delta

        temp_requirements_arr = temp_requirements_df[column_names.REQUIRED_T_AT_HOME_IN].to_numpy()
        need_boiler_t_arr = np.empty(shape=(need_boiler_t_df_len,), dtype=np.float)
        for time_moment in range(need_boiler_t_df_len):
            need_boiler_t = self._calc_need_boiler_t_for_time_moment(time_moment, temp_requirements_arr)
            need_boiler_t_arr[time_moment] = need_boiler_t

        temp_requirements_dates_list = temp_requirements_df[column_names.TIMESTAMP].to_list()
        need_boiler_t_dates_list = temp_requirements_dates_list[:need_boiler_t_df_len]
        need_boiler_t_df = pd.DataFrame({
            column_names.TIMESTAMP: need_boiler_t_dates_list,
            column_names.BOILER: need_boiler_t_arr
        })
        return need_boiler_t_df

    def _calc_need_boiler_t_for_time_moment(self, time_moment, temp_requirements_arr):
        need_boiler_t = float("-inf")

        home_names = self._homes_time_deltas[column_names.HOME_NAME]
        time_deltas = self._homes_time_deltas[column_names.TIME_DELTA]
        for home_name, home_time_delta in zip(home_names, time_deltas):
            need_home_t = temp_requirements_arr[time_moment + home_time_delta]
            need_home_t *= self._home_t_dispersion_coefficient
            need_t_condition = self._optimized_t_table[home_name] >= need_home_t
            need_boiler_t_for_home = self._optimized_t_table[need_t_condition][
                column_names.BOILER].min()
            need_boiler_t = max(need_boiler_t, need_boiler_t_for_home)

        return need_boiler_t
