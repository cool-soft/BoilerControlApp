import os

import flask
import pandas as pd
from dateutil.tz import gettz

import config
from boiler_t_prediction.boiler_t_predictor import BoilerTPredictor
from boiler_t_prediction.weather_forecast_provider import WeatherForecastProvider
from dataset_utils.io_utils import load_dataframe
from dependency_injection import add_dependency
from web_app.api_rules import API_RULES

if __name__ == '__main__':
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

    app = flask.Flask(__name__)
    for rule, kwargs in API_RULES:
        app.add_url_rule(rule, **kwargs)

    app.run(
        host=config.SERVICE_HOST,
        port=config.SERVICE_PORT,
        debug=config.FLASK_DEBUG
    )
