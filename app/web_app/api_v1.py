import logging
from typing import Optional

from dateutil.tz import gettz
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from configs import GlobalAppConfig
from dataset_utils import data_consts
from boiler_t_prediction.boiler_t_predictor import BoilerTPredictor
from dependency_injection import get_dependency
from web_app.dependencies import InputDatesRange

app_config = GlobalAppConfig()
api_router = APIRouter(prefix="/api/v1")


@api_router.get("/getPredictedBoilerT", response_class=JSONResponse, deprecated=True)
def get_predicted_boiler_t(
        dates_range: InputDatesRange = Depends(),
        timezone_name: Optional[str] = app_config.datetime_processing.boiler_control_timezone
):
    """
    Метод для получения рекомендуемой температуры, которую необходимо выставить на бойлере.
    Принимает 3 **опциональных** параметра.
    - **start_date**: Дата время начала управляющего воздействия (формат см. в конфигах).
    - **end_date**: Дата время окончания управляющего воздействия (формат см. в конфигах).
    - **timezone_name**: Имя временной зоны для обработки запроса и генерации ответа.
    По-умолчанию берется из конфигов.
    """
    logging.debug(f"(API V1) Requested predicted boiler t for dates range "
                  f"from {dates_range.start_date} to {dates_range.end_date}"
                  f"with timezone_name {timezone_name}")

    boiler_t_predictor = get_dependency(BoilerTPredictor)

    predicted_boiler_t_df = boiler_t_predictor.get_need_boiler_t(dates_range.start_date, dates_range.end_date)

    boiler_control_timezone = gettz(timezone_name)
    predicted_boiler_t_ds = []
    for _, row in predicted_boiler_t_df.iterrows():
        datetime_ = row[data_consts.TIMESTAMP_COLUMN_NAME]
        datetime_ = datetime_.astimezone(boiler_control_timezone)
        datetime_as_str = datetime_.strftime(app_config.datetime_processing.response_datetime_patterns)

        boiler_t = row[data_consts.BOILER_NAME_COLUMN_NAME]
        boiler_t = round(boiler_t, 1)

        predicted_boiler_t_ds.append((datetime_as_str, boiler_t))

    return predicted_boiler_t_ds
