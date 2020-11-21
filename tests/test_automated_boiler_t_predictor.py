
from matplotlib import pyplot as plt
from datetime import datetime

import config
import consts
from boiler_t_prediction.weather_forecast_provider import WeatherForecastProvider
from boiler_t_prediction.boiler_t_predictor import BoilerTPredictor
from boiler_t_prediction.automated_boiler_t_predictor import AutomatedBoilerTPredictor
import pandas as pd

from dataset_utils.io_utils import load_dataframe


if __name__ == '__main__':
    min_date = datetime.now()
    max_date = min_date + (20 * consts.TIME_TICK)

    homes_time_deltas = pd.read_csv(config.HOMES_DELTAS_PATH)
    max_home_time_delta = homes_time_deltas[consts.TIME_DELTA_COLUMN_NAME].max()
    optimized_t_table = load_dataframe(config.OPTIMIZED_T_TABLE_PATH)
    temp_graph = pd.read_csv(config.T_GRAPH_PATH)

    forecast_weather_t_provider = WeatherForecastProvider()

    boiler_t_predictor = BoilerTPredictor()
    boiler_t_predictor.set_homes_time_deltas(homes_time_deltas)
    boiler_t_predictor.set_optimized_t_table(optimized_t_table)
    boiler_t_predictor.set_temp_graph(temp_graph)

    automated_boiler_t_predictor = AutomatedBoilerTPredictor()
    automated_boiler_t_predictor.set_max_home_time_delta(max_home_time_delta)
    automated_boiler_t_predictor.set_boiler_t_predictor(boiler_t_predictor)
    automated_boiler_t_predictor.set_weather_forecast_provider(forecast_weather_t_provider)

    predicted_boiler_t_df = automated_boiler_t_predictor.get_boiler_t(min_date, max_date)
    predicted_boiler_t_arr = predicted_boiler_t_df[consts.BOILER_NAME_COLUMN_NAME].to_numpy()

    dates_arr = predicted_boiler_t_df[consts.TIMESTAMP_COLUMN_NAME].to_list()

    weather_t_df = forecast_weather_t_provider.get_weather_forecast(min_date, max_date)
    weather_t_arr = weather_t_df[consts.WEATHER_T_COLUMN_NAME].to_numpy()

    print(min_date, max_date)
    print(len(predicted_boiler_t_df))
    for idx, row in predicted_boiler_t_df.iterrows():
        print(row[consts.TIMESTAMP_COLUMN_NAME], row[consts.BOILER_NAME_COLUMN_NAME])

    plt.plot(dates_arr, predicted_boiler_t_arr, label="Predicted boiler t")
    plt.plot(dates_arr, weather_t_arr, label="Weather t")

    plt.legend()
    plt.show()
