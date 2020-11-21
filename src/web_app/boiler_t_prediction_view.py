
from datetime import datetime

from dateutil.tz import gettz
from flask import jsonify, request
from flask.views import View

import config
import consts
from dependency_injection import get_dependency
from dataset_utils.preprocess_utils import parse_datetime

from boiler_t_prediction.boiler_t_predictor import BoilerTPredictor


class BoilerTPredictionView(View):
    methods = ['GET']

    def __init__(self):
        self.boiler_t_predictor = get_dependency(BoilerTPredictor)
        self._boiler_control_timezone = gettz(config.BOILER_CONTROL_TIMEZONE)

    def dispatch_request(self):
        start_datetime_as_str = request.args.get("start_date")
        default_start_datetime = datetime.now(tz=self._boiler_control_timezone)
        start_datetime = self._preprocess_datetime(start_datetime_as_str, default_value=default_start_datetime)

        end_datetime_as_str = request.args.get("end_date")
        default_end_datetime = start_datetime + consts.TIME_TICK
        end_datetime = self._preprocess_datetime(end_datetime_as_str, default_value=default_end_datetime)

        predicted_boiler_t_df = self.boiler_t_predictor.get_need_boiler_t(start_datetime, end_datetime)

        predicted_boiler_t_ds = []
        for _, row in predicted_boiler_t_df.iterrows():
            boiler_t = row[consts.BOILER_NAME_COLUMN_NAME]
            datetime_ = row[consts.TIMESTAMP_COLUMN_NAME]
            datetime_as_str = datetime_.strftime(config.BOILER_CONTROL_RESPONSE_DATETIME_PATTERN)
            boiler_t = round(boiler_t, 1)
            predicted_boiler_t_ds.append((datetime_as_str, boiler_t))
        boiler_t_json = jsonify(predicted_boiler_t_ds)

        return boiler_t_json

    def _preprocess_datetime(self, datetime_as_str, default_value):
        if datetime_as_str is None:
            datetime_ = default_value
        else:
            datetime_ = parse_datetime(
                datetime_as_str,
                config.BOILER_CONTROL_REQUEST_DATETIME_PATTERNS,
                timezone=self._boiler_control_timezone
            )
        return datetime_
