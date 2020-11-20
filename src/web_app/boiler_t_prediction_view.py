
from datetime import datetime

from flask import jsonify, request
from flask.views import View

import config
import consts
from dependency_injection import get_dependency
from datasets_utils.preprocess_utils import parse_datetime

from boiler_t_prediction.automated_boiler_t_predictor import AutomatedBoilerTPredictor


class BoilerTPredictionView(View):
    methods = ['GET']

    def __init__(self):
        self._automated_boiler_t_predictor = get_dependency(AutomatedBoilerTPredictor)

    def dispatch_request(self):
        start_date = request.args.get("start_date")
        if start_date is None:
            start_date = datetime.now()
        else:
            start_date = parse_datetime(start_date, config.DATETIME_REQUESTS_PATTERNS)

        end_date = request.args.get("end_date")
        if end_date is None:
            end_date = start_date + consts.TIME_STEP
        else:
            end_date = parse_datetime(end_date, config.DATETIME_REQUESTS_PATTERNS)

        predicted_boiler_t_df = self._automated_boiler_t_predictor.get_boiler_t(start_date, end_date)
        predicted_boiler_t_arr = predicted_boiler_t_df[consts.BOILER_NAME_COLUMN_NAME].to_list()
        predicted_boiler_t_dates_arr = predicted_boiler_t_df[consts.TIMESTAMP_COLUMN_NAME].to_list()

        predicted_boiler_t_ds = []
        for datetime_, boiler_t in zip(predicted_boiler_t_dates_arr, predicted_boiler_t_arr):
            datetime_as_str = datetime_.strftime(config.DATETIME_RESPONSE_PATTERN)
            boiler_t = round(boiler_t, 1)
            predicted_boiler_t_ds.append((datetime_as_str, boiler_t))

        boiler_t_ds_json = jsonify(predicted_boiler_t_ds)
        return boiler_t_ds_json
