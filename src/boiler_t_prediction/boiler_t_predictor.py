import numpy as np
import pandas as pd

import consts


class BoilerTPredictor:

    def __init__(self):
        self._optimized_t_table = None
        self._homes_time_deltas = None
        self._temp_graph = None
        self._home_t_dispersion_coefficient = 1
        self._weather_forecast_provider = None

    def set_homes_time_deltas(self, homes_time_deltas):
        self._homes_time_deltas = homes_time_deltas

    def set_optimized_t_table(self, t_table):
        self._optimized_t_table = t_table

    def set_temp_graph(self, temp_graph):
        self._temp_graph = temp_graph

    def set_dispersion_coefficient(self, coefficient):
        self._home_t_dispersion_coefficient = coefficient

    def set_weather_forecast_provider(self, weather_forecast_provider):
        self._weather_forecast_provider = weather_forecast_provider

    def get_need_boiler_t(self, start_datetime, end_datetime):
        max_home_time_delta = self._homes_time_deltas[consts.TIME_DELTA_COLUMN_NAME].max()
        weather_forecast_end_datetime = end_datetime + (max_home_time_delta * consts.TIME_TICK)
        weather_forecast_df = self._weather_forecast_provider.get_weather_forecast(
            start_datetime, weather_forecast_end_datetime
        )

        if len(weather_forecast_df) < max_home_time_delta + 1:
            return pd.DataFrame({
                consts.TIMESTAMP_COLUMN_NAME: [],
                consts.BOILER_NAME_COLUMN_NAME: []
            })

        t_graph_requirements_df = self._get_t_graph_requirements(weather_forecast_df)
        need_boiler_t_df = self._get_need_boiler_t(t_graph_requirements_df)

        return need_boiler_t_df

    def _get_t_graph_requirements(self, weather_forecast_df):
        forecast_weather_df_len = len(weather_forecast_df)
        t_graph_requirements_arr = np.empty(shape=(forecast_weather_df_len,), dtype=np.float)

        weather_t_forecast_arr = weather_forecast_df[consts.WEATHER_T_COLUMN_NAME].to_numpy()
        for i, weather_t in enumerate(weather_t_forecast_arr):
            required_t_by_t_graph = self._get_required_t_by_t_graph_for_weather_t(weather_t)
            t_graph_requirements_arr[i] = required_t_by_t_graph

        t_graph_requirements_dates_list = weather_forecast_df[consts.TIMESTAMP_COLUMN_NAME].to_list()
        t_graph_requirements_df = pd.DataFrame({
            consts.TIMESTAMP_COLUMN_NAME: t_graph_requirements_dates_list,
            consts.REQUIRED_T_IN_HOME_COLUMN_NAME: t_graph_requirements_arr
        })

        return t_graph_requirements_df

    def _get_required_t_by_t_graph_for_weather_t(self, weather_t):
        available_t_condition = self._temp_graph[consts.WEATHER_T_COLUMN_NAME] <= weather_t
        available_t = self._temp_graph[available_t_condition]
        need_t_in_home_by_t_graph = available_t[consts.REQUIRED_T_IN_HOME_COLUMN_NAME].min()
        return need_t_in_home_by_t_graph

    def _get_need_boiler_t(self, t_graph_requirements_df):
        max_home_time_delta = self._homes_time_deltas[consts.TIME_DELTA_COLUMN_NAME].max()
        need_boiler_t_df_len = len(t_graph_requirements_df) - max_home_time_delta

        t_graph_requirements_arr = t_graph_requirements_df[consts.REQUIRED_T_IN_HOME_COLUMN_NAME].to_numpy()
        need_boiler_t_arr = np.empty(shape=(need_boiler_t_df_len,), dtype=np.float)
        for time_moment in range(need_boiler_t_df_len):
            need_boiler_t = self._calc_need_boiler_t_for_time_moment(time_moment, t_graph_requirements_arr)
            need_boiler_t_arr[time_moment] = need_boiler_t

        t_graph_requirements_dates_list = t_graph_requirements_df[consts.TIMESTAMP_COLUMN_NAME].to_list()
        need_boiler_t_dates_list = t_graph_requirements_dates_list[:need_boiler_t_df_len]
        need_boiler_t_df = pd.DataFrame({
            consts.TIMESTAMP_COLUMN_NAME: need_boiler_t_dates_list,
            consts.BOILER_NAME_COLUMN_NAME: need_boiler_t_arr
        })
        return need_boiler_t_df

    def _calc_need_boiler_t_for_time_moment(self, time_moment, t_graph_requirements_arr):
        need_boiler_t = float("-inf")

        home_names = self._homes_time_deltas[consts.HOME_NAME_COLUMN_NAME]
        time_deltas = self._homes_time_deltas[consts.TIME_DELTA_COLUMN_NAME]
        for home_name, home_time_delta in zip(home_names, time_deltas):
            need_home_t = t_graph_requirements_arr[time_moment + home_time_delta]
            need_home_t *= self._home_t_dispersion_coefficient
            need_t_condition = self._optimized_t_table[home_name] >= need_home_t
            need_boiler_t_for_home = self._optimized_t_table[need_t_condition][consts.BOILER_NAME_COLUMN_NAME].min()
            need_boiler_t = max(need_boiler_t, need_boiler_t_for_home)

        return need_boiler_t
