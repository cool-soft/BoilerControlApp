import pandas as pd

import column_names
from preprocess_utils import arithmetic_round

if __name__ == '__main__':

    temp_graph_df = pd.read_csv("../storage/temp_graph.csv", )


    def get_required_temp_by_temp_graph(weather_temp, temp_graph):
        weather_temp = arithmetic_round(weather_temp)
        available_temp_condition = temp_graph[column_names.WEATHER_TEMP] <= weather_temp
        available_temp = temp_graph[available_temp_condition]
        if not available_temp.empty:
            required_temp_idx = available_temp[column_names.WEATHER_TEMP].idxmax()
        else:
            required_temp_idx = temp_graph[column_names.WEATHER_TEMP].idxmin()
        required_temp = temp_graph.loc[required_temp_idx]

        return required_temp.copy()

    print(type(get_required_temp_by_temp_graph(-150, temp_graph_df)))
    required_temp = get_required_temp_by_temp_graph(-150, temp_graph_df)
    print(required_temp[column_names.REQUIRED_TEMP_AT_HOME_IN])
    print(get_required_temp_by_temp_graph(-150, temp_graph_df))
    print(get_required_temp_by_temp_graph(50, temp_graph_df))
    print(get_required_temp_by_temp_graph(-20.5, temp_graph_df))
    print(get_required_temp_by_temp_graph(-20.6, temp_graph_df))
