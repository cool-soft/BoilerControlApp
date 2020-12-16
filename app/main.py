import logging
import os

import pandas as pd
import uvicorn
from dateutil.tz import gettz
from fastapi import FastAPI

import config
from boiler_t_prediction.boiler_t_predictor import BoilerTPredictor
from boiler_t_prediction.weather_forecast_provider import WeatherForecastProvider
from dataset_utils.io_utils import load_dataframe
from dependency_injection import add_dependency
from web_app.api_v1 import app as api_v1
from web_app.api_v2 import app as api_v2

if __name__ == '__main__':
    logging.basicConfig(
        filename=config.LOG_PATH,
        level=config.LOG_LEVEL,
        datefmt=config.LOG_DATETIME_FORMAT,
        format=config.LOG_FORMAT
    )

    optimized_t_table = load_dataframe(config.OPTIMIZED_T_TABLE_PATH)
    temp_graph = pd.read_csv(os.path.abspath(config.T_GRAPH_PATH))
    homes_time_deltas = pd.read_csv(os.path.abspath(config.HOMES_DELTAS_PATH))

    weather_forecast_provider = WeatherForecastProvider()
    weather_forecast_provider.set_weather_forecast_server_timezone(gettz(config.WEATHER_FORECAST_SERVER_TIMEZONE))
    weather_forecast_provider.set_weather_forecast_server_address(config.WEATHER_FORECAST_SERVER_ADDRESS)
    weather_forecast_provider.set_weather_forecast_update_interval(config.WEATHER_FORECAST_UPDATE_INTERVAL)

    boiler_t_predictor = BoilerTPredictor()
    boiler_t_predictor.set_optimized_t_table(optimized_t_table)
    boiler_t_predictor.set_temp_graph(temp_graph)
    boiler_t_predictor.set_homes_time_deltas(homes_time_deltas)
    boiler_t_predictor.set_weather_forecast_provider(weather_forecast_provider)

    add_dependency(boiler_t_predictor)

    app = FastAPI()
    app.mount("/api/v1", api_v1)
    app.mount("/api/v2", api_v2)
    uvicorn.run(
        app,
        host=config.SERVICE_HOST,
        port=config.SERVICE_PORT
    )
