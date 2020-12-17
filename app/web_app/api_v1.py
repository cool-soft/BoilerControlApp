from dateutil.tz import gettz
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

import config
import consts
from boiler_t_prediction.boiler_t_predictor import BoilerTPredictor
from dependency_injection import get_dependency
from web_app.dependencies import InputDatesRange

api_router = APIRouter(prefix="/api/v1")


@api_router.get("/getPredictedBoilerT", response_class=JSONResponse, deprecated=True)
def get_predicted_boiler_t(dates_range: InputDatesRange = Depends()):
    """
    Метод для получения рекомендуемой температуры, которую необходимо выставить на бойлере.
    """

    boiler_t_predictor = get_dependency(BoilerTPredictor)

    predicted_boiler_t_df = boiler_t_predictor.get_need_boiler_t(dates_range.start_date, dates_range.end_date)

    boiler_control_timezone = gettz(config.BOILER_CONTROL_TIMEZONE)
    predicted_boiler_t_ds = []
    for _, row in predicted_boiler_t_df.iterrows():
        datetime_ = row[consts.TIMESTAMP_COLUMN_NAME]
        datetime_ = datetime_.astimezone(boiler_control_timezone)
        datetime_as_str = datetime_.strftime(config.BOILER_CONTROL_RESPONSE_DATETIME_PATTERN)

        boiler_t = row[consts.BOILER_NAME_COLUMN_NAME]
        boiler_t = round(boiler_t, 1)

        predicted_boiler_t_ds.append((datetime_as_str, boiler_t))

    return predicted_boiler_t_ds
