import logging
import os

import numpy as np
import pandas as pd

from boiler_t_prediction.weather_forecast_provider import WeatherForecastProvider
from configs.boiler_t_predictor_config import BoilerTPredictorConfig
from dataset_utils import data_consts
from dataset_utils.io_utils import load_dataframe


class BoilerTPredictor:

    def __init__(self):
        logging.debug("Initialization of BoilerTPredictor")
        self._optimized_t_table = None
        self._homes_time_deltas = None
        self._temp_graph = None
        self._home_t_dispersion_coefficient = 1
        self._weather_forecast_provider = None

    def set_homes_time_deltas(self, homes_time_deltas):
        logging.debug("Set homes time deltas")
        self._homes_time_deltas = homes_time_deltas

    def set_optimized_t_table(self, t_table):
        logging.debug("Set optimized t table")
        self._optimized_t_table = t_table

    def set_temp_graph(self, temp_graph):
        logging.debug("Set temp graph")
        self._temp_graph = temp_graph

    def set_dispersion_coefficient(self, coefficient):
        logging.debug(f"Set dispersion coefficient to {coefficient}")
        self._home_t_dispersion_coefficient = coefficient

    def set_weather_forecast_provider(self, weather_forecast_provider):
        logging.debug("Set weather forecast provider")
        self._weather_forecast_provider = weather_forecast_provider

    def get_need_boiler_t(self, start_datetime, end_datetime):
        logging.debug(f"Requested predicted boiler t from {start_datetime.isoformat()} to {end_datetime.isoformat()}")

        max_home_time_delta = self._homes_time_deltas[data_consts.TIME_DELTA_COLUMN_NAME].max()
        weather_forecast_end_datetime = end_datetime + (max_home_time_delta * data_consts.TIME_TICK)
        weather_forecast_df = self._weather_forecast_provider.get_weather_forecast(
            start_datetime, weather_forecast_end_datetime
        )

        if len(weather_forecast_df) < max_home_time_delta + 1:
            return pd.DataFrame({
                data_consts.TIMESTAMP_COLUMN_NAME: [],
                data_consts.BOILER_NAME_COLUMN_NAME: []
            })

        t_graph_requirements_df = self._get_t_graph_requirements(weather_forecast_df)
        need_boiler_t_df = self._get_need_boiler_t(t_graph_requirements_df)

        return need_boiler_t_df

    def _get_t_graph_requirements(self, weather_forecast_df):
        logging.debug(f"Requested calculation of t graph requirements")

        forecast_weather_df_len = len(weather_forecast_df)
        t_graph_requirements_arr = np.empty(shape=(forecast_weather_df_len,), dtype=np.float)

        weather_t_forecast_arr = weather_forecast_df[data_consts.WEATHER_T_COLUMN_NAME].to_numpy()
        for i, weather_t in enumerate(weather_t_forecast_arr):
            required_t_by_t_graph = self._get_required_t_by_t_graph_for_weather_t(weather_t)
            t_graph_requirements_arr[i] = required_t_by_t_graph

        t_graph_requirements_dates_list = weather_forecast_df[data_consts.TIMESTAMP_COLUMN_NAME].to_list()
        t_graph_requirements_df = pd.DataFrame({
            data_consts.TIMESTAMP_COLUMN_NAME: t_graph_requirements_dates_list,
            data_consts.REQUIRED_T_AT_HOME_IN_COLUMN_NAME: t_graph_requirements_arr
        })

        return t_graph_requirements_df

    def _get_required_t_by_t_graph_for_weather_t(self, weather_t):
        available_t_condition = self._temp_graph[data_consts.WEATHER_T_COLUMN_NAME] <= weather_t
        available_t = self._temp_graph[available_t_condition]
        need_t_in_home_by_t_graph = available_t[data_consts.REQUIRED_T_AT_HOME_IN_COLUMN_NAME].min()
        return need_t_in_home_by_t_graph

    def _get_need_boiler_t(self, t_graph_requirements_df):
        logging.debug(f"Requested need boiler t for t graph requirements")

        max_home_time_delta = self._homes_time_deltas[data_consts.TIME_DELTA_COLUMN_NAME].max()
        need_boiler_t_df_len = len(t_graph_requirements_df) - max_home_time_delta

        t_graph_requirements_arr = t_graph_requirements_df[data_consts.REQUIRED_T_AT_HOME_IN_COLUMN_NAME].to_numpy()
        need_boiler_t_arr = np.empty(shape=(need_boiler_t_df_len,), dtype=np.float)
        for time_moment in range(need_boiler_t_df_len):
            need_boiler_t = self._calc_need_boiler_t_for_time_moment(time_moment, t_graph_requirements_arr)
            need_boiler_t_arr[time_moment] = need_boiler_t

        t_graph_requirements_dates_list = t_graph_requirements_df[data_consts.TIMESTAMP_COLUMN_NAME].to_list()
        need_boiler_t_dates_list = t_graph_requirements_dates_list[:need_boiler_t_df_len]
        need_boiler_t_df = pd.DataFrame({
            data_consts.TIMESTAMP_COLUMN_NAME: need_boiler_t_dates_list,
            data_consts.BOILER_NAME_COLUMN_NAME: need_boiler_t_arr
        })
        return need_boiler_t_df

    def _calc_need_boiler_t_for_time_moment(self, time_moment, t_graph_requirements_arr):
        need_boiler_t = float("-inf")

        home_names = self._homes_time_deltas[data_consts.HOME_NAME_COLUMN_NAME]
        time_deltas = self._homes_time_deltas[data_consts.TIME_DELTA_COLUMN_NAME]
        for home_name, home_time_delta in zip(home_names, time_deltas):
            need_home_t = t_graph_requirements_arr[time_moment + home_time_delta]
            need_home_t *= self._home_t_dispersion_coefficient
            need_t_condition = self._optimized_t_table[home_name] >= need_home_t
            need_boiler_t_for_home = self._optimized_t_table[need_t_condition][
                data_consts.BOILER_NAME_COLUMN_NAME].min()
            need_boiler_t = max(need_boiler_t, need_boiler_t_for_home)

        return need_boiler_t

    @classmethod
    def from_config(cls, config: BoilerTPredictorConfig):
        boiler_t_predictor = cls()

        optimized_t_table_path = os.path.abspath(config.optimized_t_table_path)
        logging.debug(f"Loading optimized t table from {optimized_t_table_path}")
        optimized_t_table = load_dataframe(optimized_t_table_path)
        boiler_t_predictor.set_optimized_t_table(optimized_t_table)

        t_graph_path = os.path.abspath(config.t_graph_path)
        logging.debug(f"Loading optimized t graph from {t_graph_path}")
        temp_graph = pd.read_csv(t_graph_path)
        boiler_t_predictor.set_temp_graph(temp_graph)

        homes_deltas_path = os.path.abspath(config.homes_deltas_path)
        logging.debug(f"Home time deltas from {homes_deltas_path}")
        homes_time_deltas = pd.read_csv(homes_deltas_path)
        boiler_t_predictor.set_homes_time_deltas(homes_time_deltas)

        weather_forecast_provider = WeatherForecastProvider.from_config(config.weather_forecast_provider)
        boiler_t_predictor.set_weather_forecast_provider(weather_forecast_provider)

        boiler_t_predictor.set_dispersion_coefficient(config.home_t_dispersion_coefficient)

        return boiler_t_predictor
