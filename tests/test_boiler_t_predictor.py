import os
import pickle

from dateutil.tz import gettz
from matplotlib import pyplot as plt
from datetime import datetime

from configs.app_config import GlobalAppConfig
import column_names
import time_tick
from services.weather_service.online_soft_m_weather_service import OnlineSoftMWeatherService
from services.boiler_temp_prediction_service.simple_boiler_temp_prediction_service import SimpleBoilerTempPredictionService
import pandas as pd


if __name__ == '__main__':
    app_config = GlobalAppConfig.load_app_config()

    min_date = datetime.now(tz=gettz(app_config.datetime_processing.boiler_controller_timezone))
    max_date = min_date + (100 * time_tick.TIME_TICK)

    with open(app_config.boiler_t_predictor.optimized_t_table_path, "rb") as f:
        optimized_t_table = pickle.load(f)
    temp_graph = pd.read_csv(os.path.abspath(app_config.boiler_t_predictor.t_graph_path))
    homes_time_deltas = pd.read_csv(app_config.boiler_t_predictor.homes_deltas_path)
    max_home_time_delta = homes_time_deltas[column_names.TIME_DELTA].max()

    weather_forecast_provider = OnlineSoftMWeatherService()
    weather_forecast_provider.set_server_timezone(
        gettz(app_config.weather_forecast_provider.server_timezone))
    weather_forecast_provider.set_server_address(app_config.weather_forecast_provider.server_address)

    boiler_t_predictor = SimpleBoilerTempPredictionService()
    boiler_t_predictor.set_temp_correlation_table(optimized_t_table)
    boiler_t_predictor.set_temp_requirements_service(temp_graph)
    boiler_t_predictor.set_homes_time_deltas(homes_time_deltas)
    boiler_t_predictor.set_weather_forecast_service(weather_forecast_provider)

    predicted_boiler_t_df = boiler_t_predictor.get_need_boiler_t(min_date, max_date)
    predicted_boiler_t_arr = predicted_boiler_t_df[column_names.BOILER_OUT_TEMP].to_numpy()

    dates_arr = predicted_boiler_t_df[column_names.TIMESTAMP].to_list()

    weather_t_df = weather_forecast_provider.get_weather(min_date, max_date)
    weather_t_arr = weather_t_df[column_names.WEATHER_TEMP].to_numpy()
    weather_t_arr = weather_t_arr[:len(predicted_boiler_t_arr)]

    for idx, row in predicted_boiler_t_df.iterrows():
        print(row[column_names.TIMESTAMP], round(row[column_names.BOILER_OUT_TEMP], 1))

    plt.plot(dates_arr, predicted_boiler_t_arr, label="Predicted boiler t")
    plt.plot(dates_arr, weather_t_arr, label="Weather t")

    plt.legend()
    plt.show()
