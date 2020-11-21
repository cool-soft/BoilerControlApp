
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

    def get_boiler_t(self, start_datetime, end_datetime):
        max_home_time_delta = self._homes_time_deltas[consts.TIME_DELTA_COLUMN_NAME].max()

        t_graph_requirements_end_datetime = end_datetime + (max_home_time_delta * consts.TIME_TICK)
        t_graph_requirements_df = self._get_t_graph_requirements(start_datetime, t_graph_requirements_end_datetime)

        predicted_boiler_t_count = len(t_graph_requirements_df) - max_home_time_delta

        t_graph_requirements_arr = t_graph_requirements_df[consts.HOME_T_COLUMN_NAME].to_numpy()
        predicted_boiler_t_arr = np.empty(shape=(predicted_boiler_t_count,), dtype=np.float)
        for idx in range(predicted_boiler_t_count):
            need_t_by_homes = self._get_need_t_in_homes(idx, t_graph_requirements_arr)
            need_boiler_t = self._calc_need_boiler_t_by_homes_t(need_t_by_homes)
            predicted_boiler_t_arr[idx] = need_boiler_t

        t_graph_requirements_datetime_list = t_graph_requirements_df[consts.TIMESTAMP_COLUMN_NAME].to_list()
        predicted_boiler_t_dates = t_graph_requirements_datetime_list[:predicted_boiler_t_count]

        predicted_boiler_t_df = pd.DataFrame({
            consts.BOILER_NAME_COLUMN_NAME: predicted_boiler_t_arr,
            consts.TIMESTAMP_COLUMN_NAME: predicted_boiler_t_dates
        })

        return predicted_boiler_t_df

    def _get_t_graph_requirements(self, start_datetime, end_datetime):
        weather_forecast_df = self._weather_forecast_provider.get_weather_forecast(start_datetime, end_datetime)
        weather_t_forecast_arr = weather_forecast_df[consts.WEATHER_T_COLUMN_NAME].to_numpy()

        weather_t_forecast_len = len(weather_t_forecast_arr)
        t_graph_requirements_arr = np.empty(shape=(weather_t_forecast_len,), dtype=np.float)
        for i in range(weather_t_forecast_len):
            weather_t = weather_t_forecast_arr[i]
            need_t_in_home_by_t_graph = self._get_need_t_by_temp_graph(weather_t)
            t_graph_requirements_arr[i] = need_t_in_home_by_t_graph

        t_graph_requirements_dates_list = weather_forecast_df[consts.TIMESTAMP_COLUMN_NAME].to_list()
        t_graph_requirements_df = pd.DataFrame({
            consts.TIMESTAMP_COLUMN_NAME: t_graph_requirements_dates_list,
            consts.HOME_T_COLUMN_NAME: t_graph_requirements_arr
        })

        return t_graph_requirements_df

    def _get_need_t_by_temp_graph(self, weather_t):
        available_t_condition = self._temp_graph[consts.WEATHER_T_COLUMN_NAME] <= weather_t
        available_t = self._temp_graph[available_t_condition]
        need_t_in_home_by_t_graph = available_t[consts.HOME_T_COLUMN_NAME].min()
        return need_t_in_home_by_t_graph

    def _get_need_t_in_homes(self, t_idx, t_graph_requirements_arr):
        need_temps = {}
        for index, row in self._homes_time_deltas.iterrows():
            home_time_delta = row[consts.TIME_DELTA_COLUMN_NAME]
            home_name = row[consts.HOME_NAME_COLUMN_NAME]

            need_t = t_graph_requirements_arr[t_idx + home_time_delta]
            need_temps[home_name] = need_t

        return need_temps

    def _calc_need_boiler_t_by_homes_t(self, need_t_by_homes):
        iterator = iter(need_t_by_homes.items())
        home_name, need_home_t = next(iterator)
        need_t_condition = self._optimized_t_table[home_name] >= need_home_t
        for home_name, need_home_t in iterator:
            need_t_condition = need_t_condition & (self._optimized_t_table[home_name] >= need_home_t)

        need_boiler_t = self._optimized_t_table[need_t_condition][consts.BOILER_NAME_COLUMN_NAME].min()
        return need_boiler_t
