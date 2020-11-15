
import pandas as pd
import numpy as np

from config import T_GRAPH_PATH, HOME_T_DISPERSION_COEFFICIENT


def calc_need_t_in_home(
        weather_t_arr,
        t_graph=None,
        home_t_dispersion_coefficient=HOME_T_DISPERSION_COEFFICIENT
):
    if t_graph is None:
        t_graph = load_t_graph()

    need_t_count = len(weather_t_arr)
    need_t_arr = np.empty(need_t_count)
    for i in range(need_t_count):
        weather_t_moment = weather_t_arr[i]
        available_t = t_graph[t_graph["weather_t"] <= weather_t_moment]
        need_t = available_t["home_t"].min() * home_t_dispersion_coefficient
        need_t_arr[i] = need_t
    return need_t_arr


def load_t_graph(path=T_GRAPH_PATH):
    t_graph_df = pd.read_csv(path)
    return t_graph_df
