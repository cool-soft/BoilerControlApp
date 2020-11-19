
from matplotlib import pyplot as plt
from datetime import datetime

import config
from modules import consts
from modules.boiler_t_prediction.forecast_weather_t_provider import ForecastWeatherTProvider
from modules.boiler_t_prediction.boiler_t_predictor import BoilerTPredictor
import pandas as pd

from modules.datasets_utils.io_utils import load_dataframe

if __name__ == '__main__':
    min_date = datetime.now()
    max_date = min_date + (60 * consts.TIME_STEP)

    prediction_step = 3

    homes_time_deltas = pd.read_csv(config.HOMES_DELTAS_PATH)
    optimized_t_table = load_dataframe(config.OPTIMIZED_T_TABLE_PATH)
    temp_graph = pd.read_csv(config.T_GRAPH_PATH)

    forecast_weather_t_provider = ForecastWeatherTProvider()
    forecast_weather_t_df = forecast_weather_t_provider.get_forecast_weather_t(min_date, max_date)
    forecast_weather_t = forecast_weather_t_df[consts.WEATHER_T_COLUMN_NAME].to_numpy()

    boiler_t_predictor = BoilerTPredictor()
    boiler_t_predictor.set_homes_time_deltas(homes_time_deltas)
    boiler_t_predictor.set_optimized_t_table(optimized_t_table)
    boiler_t_predictor.set_temp_graph(temp_graph)

    predicted_boiler_t = boiler_t_predictor.predict_on_weather_t_arr(forecast_weather_t)
    dates = forecast_weather_t_df[consts.TIMESTAMP_COLUMN_NAME].to_list()
    dates = dates[:len(predicted_boiler_t)]

    plt.plot(dates, predicted_boiler_t, label="Predicted boiler t")
    plt.plot(dates, forecast_weather_t[:len(predicted_boiler_t)], label="Weather t")

    plt.legend()
    plt.show()
