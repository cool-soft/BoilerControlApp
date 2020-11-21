
from datetime import datetime

import pandas as pd

import consts
from dataset_utils.preprocess_utils import round_datetime, sort_by_timestamp


class AutomatedBoilerTPredictor:

    def __init__(self):
        self._boiler_t_predictor = None
        self._weather_forecast_provider = None
        self._max_home_time_delta = 0

    def set_max_home_time_delta(self, delta):
        self._max_home_time_delta = delta

    def set_weather_forecast_provider(self, forecast_weather_t_provider):
        self._weather_forecast_provider = forecast_weather_t_provider

    def set_boiler_t_predictor(self, boiler_t_predictor):
        self._boiler_t_predictor = boiler_t_predictor

    def get_boiler_t(self, start_date=None, end_date=None):
        if start_date is None:
            start_date = datetime.now()
        start_date = round_datetime(start_date)

        if end_date is None:
            end_date = start_date + consts.TIME_STEP
        end_date = round_datetime(end_date)

        end_date = end_date + (self._max_home_time_delta * consts.TIME_STEP)

        weather_forecast_df = self._weather_forecast_provider.get_weather_forecast(start_date, end_date)
        sorted_weather_forecast_df = sort_by_timestamp(weather_forecast_df)
        predicted_boiler_t_arr = self._boiler_t_predictor.predict_on_weather_forecast(sorted_weather_forecast_df)

        forecast_weather_t_dates = weather_forecast_df[consts.TIMESTAMP_COLUMN_NAME].to_list()
        predicted_boiler_t_dates = forecast_weather_t_dates[:len(predicted_boiler_t_arr)]

        predicted_boiler_t_df = pd.DataFrame({
            consts.BOILER_NAME_COLUMN_NAME: predicted_boiler_t_arr,
            consts.TIMESTAMP_COLUMN_NAME: predicted_boiler_t_dates
        })

        return predicted_boiler_t_df
