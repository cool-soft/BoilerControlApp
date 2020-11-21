import os

import pandas as pd
import flask

import config
import consts
from boiler_t_prediction.forecast_weather_t_provider import ForecastWeatherTProvider
from boiler_t_prediction.boiler_t_predictor import BoilerTPredictor
from boiler_t_prediction.automated_boiler_t_predictor import AutomatedBoilerTPredictor
from dataset_utils.io_utils import load_dataframe
from dependency_injection import add_dependency
from web_app.api_rules import API_RULES


if __name__ == '__main__':
    homes_time_deltas = pd.read_csv(config.HOMES_DELTAS_PATH)
    optimized_t_table = load_dataframe(config.OPTIMIZED_T_TABLE_PATH)
    temp_graph = pd.read_csv(os.path.abspath(config.T_GRAPH_PATH))

    boiler_t_predictor = BoilerTPredictor()
    boiler_t_predictor.set_optimized_t_table(optimized_t_table)
    boiler_t_predictor.set_temp_graph(temp_graph)
    boiler_t_predictor.set_homes_time_deltas(homes_time_deltas)

    forecast_weather_t_provider = ForecastWeatherTProvider()

    max_home_time_delta = homes_time_deltas[consts.TIME_DELTA_COLUMN_NAME].max()

    automated_boiler_t_predictor = AutomatedBoilerTPredictor()
    automated_boiler_t_predictor.set_max_home_time_delta(max_home_time_delta)
    automated_boiler_t_predictor.set_boiler_t_predictor(boiler_t_predictor)
    automated_boiler_t_predictor.set_forecast_weather_t_provider(forecast_weather_t_provider)

    add_dependency(automated_boiler_t_predictor)

    app = flask.Flask(__name__)
    for rule, kwargs in API_RULES:
        app.add_url_rule(rule, **kwargs)

    app.run(port=config.SERVICE_PORT, debug=config.FLASK_DEBUG)
