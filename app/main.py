import logging
import os

import pandas as pd
import uvicorn
from dateutil.tz import gettz
from fastapi import FastAPI

from boiler_t_prediction.boiler_t_predictor import BoilerTPredictor
from boiler_t_prediction.weather_forecast_provider import WeatherForecastProvider
from configs import GlobalAppConfig
from dataset_utils.io_utils import load_dataframe
from dependency_injection import add_dependency
from web_app.api_v1 import api_router as api_v1
from web_app.api_v2 import api_router as api_v2

if __name__ == '__main__':
    config = GlobalAppConfig.load_app_config()

    logging.basicConfig(
        filename=config.logging.path,
        level=config.logging.level,
        datefmt=config.logging.datetime_format,
        format=config.logging.format
    )

    OPTIMIZED_T_TABLE_PATH = os.path.abspath(config.boiler_t_prediction.optimized_t_table_path)
    logging.debug(f"Loading optimized t table from {OPTIMIZED_T_TABLE_PATH}")
    optimized_t_table = load_dataframe(OPTIMIZED_T_TABLE_PATH)

    T_GRAPH_PATH = os.path.abspath(config.boiler_t_prediction.t_graph_path)
    logging.debug(f"Loading optimized t graph from {T_GRAPH_PATH}")
    temp_graph = pd.read_csv(T_GRAPH_PATH)

    HOMES_DELTAS_PATH = os.path.abspath(config.boiler_t_prediction.homes_deltas_path)
    logging.debug(f"Home time deltas from {HOMES_DELTAS_PATH}")
    homes_time_deltas = pd.read_csv(HOMES_DELTAS_PATH)

    logging.debug("Initialization of WeatherForecastProvider")
    weather_forecast_provider = WeatherForecastProvider()
    weather_forecast_server_timezone = gettz(config.weather_forecast_providing.server_timezone)
    weather_forecast_provider.set_weather_forecast_server_timezone(weather_forecast_server_timezone)
    weather_forecast_provider.set_weather_forecast_server_address(
        config.weather_forecast_providing.server_address
    )
    weather_forecast_provider.set_weather_forecast_update_interval(
        config.weather_forecast_providing.update_interval
    )

    logging.debug("Initialization of BoilerTPredictor")
    boiler_t_predictor = BoilerTPredictor()
    boiler_t_predictor.set_optimized_t_table(optimized_t_table)
    boiler_t_predictor.set_temp_graph(temp_graph)
    boiler_t_predictor.set_homes_time_deltas(homes_time_deltas)
    boiler_t_predictor.set_weather_forecast_provider(weather_forecast_provider)
    boiler_t_predictor.set_dispersion_coefficient(
        config.boiler_t_prediction.home_t_dispersion_coefficient
    )

    add_dependency(boiler_t_predictor)

    app = FastAPI()
    app.include_router(api_v1)
    app.include_router(api_v2)
    uvicorn.run(
        app,
        host=config.service.host,
        port=config.service.port
    )
