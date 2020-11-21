
from datetime import datetime

import pandas as pd

import consts
from dataset_utils.preprocess_utils import round_datetime


class AutomatedBoilerTPredictor:

    def __init__(self):
        self._boiler_t_predictor = None
        self._forecast_weather_t_provider = None
        self._max_home_time_delta = 0

    def set_max_home_time_delta(self, delta):
        self._max_home_time_delta = delta

    def set_forecast_weather_t_provider(self, forecast_weather_t_provider):
        self._forecast_weather_t_provider = forecast_weather_t_provider

    def set_boiler_t_predictor(self, boiler_t_predictor):
        self._boiler_t_predictor = boiler_t_predictor

    def get_boiler_t(self, min_date=None, max_date=None):
        if min_date is None:
            min_date = datetime.now()
        min_date = round_datetime(min_date)

        if max_date is None:
            max_date = min_date + consts.TIME_STEP
        max_date = round_datetime(max_date)

        max_date = max_date + (self._max_home_time_delta * consts.TIME_STEP)

        forecast_weather_t_df = self._forecast_weather_t_provider.get_weather_forecast(min_date, max_date)
        forecast_weather_t = forecast_weather_t_df[consts.WEATHER_T_COLUMN_NAME].to_numpy()

        predicted_boiler_t_arr = self._boiler_t_predictor.predict_on_weather_t_arr(forecast_weather_t)

        forecast_weather_t_dates = forecast_weather_t_df[consts.TIMESTAMP_COLUMN_NAME].to_list()
        predicted_boiler_t_dates = forecast_weather_t_dates[:len(predicted_boiler_t_arr)]

        predicted_boiler_t_df = pd.DataFrame({
            consts.BOILER_NAME_COLUMN_NAME: predicted_boiler_t_arr,
            consts.TIMESTAMP_COLUMN_NAME: predicted_boiler_t_dates
        })

        return predicted_boiler_t_df
