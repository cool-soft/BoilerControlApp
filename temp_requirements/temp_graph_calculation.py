import logging

import pandas as pd

from heating_system import column_names
from heating_system.preprocess_utils import arithmetic_round


def get_required_temp_by_temp_graph_for_weather_temp_arr(weather_temp_arr, temp_graph):
    required_temp_list = []
    for weather_temp in weather_temp_arr:
        required_temp = get_required_temp_by_temp_graph_for_weather_temp(weather_temp, temp_graph)
        required_temp_list.append(required_temp)
    required_temp_df = pd.DataFrame(required_temp_list)
    return required_temp_df


def get_required_temp_by_temp_graph_for_weather_temp(weather_temp, temp_graph):
    weather_temp = arithmetic_round(weather_temp)

    available_temp_condition = temp_graph[column_names.WEATHER_TEMP] <= weather_temp
    available_temp = temp_graph[available_temp_condition]
    if not available_temp.empty:
        required_temp_idx = available_temp[column_names.WEATHER_TEMP].idxmax()

    else:
        required_temp_idx = temp_graph[column_names.WEATHER_TEMP].idxmin()
        logging.debug(f"Weather temp {weather_temp} is not in temp graph.")

    required_temp = temp_graph.loc[required_temp_idx]
    return required_temp.copy()
