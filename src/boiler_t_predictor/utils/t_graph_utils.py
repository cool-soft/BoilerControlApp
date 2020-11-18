
import pandas as pd
import numpy as np

import config
import consts


def calc_need_t_in_home(
        weather_t_arr,
        t_graph,
        home_t_dispersion_coefficient=config.HOME_T_DISPERSION_COEFFICIENT
):
    need_home_t_count = len(weather_t_arr)
    need_home_t_arr = np.empty(need_home_t_count)
    for i in range(need_home_t_count):
        weather_t = weather_t_arr[i]
        available_t = t_graph[t_graph[consts.WEATHER_T_COLUMN_NAME] <= weather_t]
        need_home_t = available_t[consts.HOME_T_COLUMN_NAME].min() * home_t_dispersion_coefficient
        need_home_t_arr[i] = need_home_t
    return need_home_t_arr


def load_t_graph(path=config.T_GRAPH_PATH):
    t_graph_df = pd.read_csv(path)
    return t_graph_df
