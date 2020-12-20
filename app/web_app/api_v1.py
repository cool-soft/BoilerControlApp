import logging
from typing import Optional

from dateutil.tz import gettz
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from boiler_t_predictor_service import BoilerTPredictorService
from containers.services import Services
from dataset_utils import data_consts
from web_app.dependencies import InputDatesRange

api_router = APIRouter(prefix="/api/v1")


@api_router.get("/getPredictedBoilerT", response_class=JSONResponse, deprecated=True)
@inject
def get_predicted_boiler_t(
        dates_range: InputDatesRange = Depends(),
        timezone_name: Optional[str] = "Asia/Yekaterinburg",
        boiler_t_predictor: BoilerTPredictorService = Depends(Provide[Services.boiler_t_predictor_service])
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

    predicted_boiler_t_df = boiler_t_predictor.get_need_boiler_t(dates_range.start_date, dates_range.end_date)

    boiler_control_timezone = gettz(timezone_name)
    predicted_boiler_t_ds = []
    for _, row in predicted_boiler_t_df.iterrows():
        datetime_ = row[data_consts.TIMESTAMP_COLUMN_NAME]
        datetime_ = datetime_.astimezone(boiler_control_timezone)
        datetime_as_str = datetime_.strftime('%Y-%m-%d %H:%M')

        boiler_t = row[data_consts.BOILER_NAME_COLUMN_NAME]
        boiler_t = round(boiler_t, 1)

        predicted_boiler_t_ds.append((datetime_as_str, boiler_t))

    return predicted_boiler_t_ds
