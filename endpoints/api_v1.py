import logging
from typing import Optional

from dateutil.tz import gettz
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from constants import column_names
from services.boiler_temp_prediction_service.boiler_temp_prediction_service \
    import BoilerTempPredictionService
from containers.core import Core
from containers.services import Services
from endpoints.dependencies import InputDatesRange

api_router = APIRouter(prefix="/api/v1")


@api_router.get("/getPredictedBoilerT", response_class=JSONResponse, deprecated=True)
@inject
def get_predicted_boiler_t(
        dates_range: InputDatesRange = Depends(),
        timezone_name: Optional[str] = None,
        boiler_t_predictor: BoilerTempPredictionService = Depends(
            Provide[Services.boiler_temp_prediction.boiler_temp_prediction_service]
        ),
        datetime_processing_params=Depends(Provide[Core.config.datetime_processing])
):
    """
    Метод для получения рекомендуемой температуры, которую необходимо выставить на бойлере.
    Принимает 3 **опциональных** параметра.
    - **start_date**: Дата время начала управляющего воздействия (формат см. в конфигах).
    - **end_date**: Дата время окончания управляющего воздействия (формат см. в конфигах).
    - **timezone_name**: Имя временной зоны для обработки запроса и генерации ответа.
    По-умолчанию берется из конфигов.
    """
    _logger = logging.getLogger(__name__)
    _logger.debug(f"Requested predicted boiler t for dates range "
                  f"from {dates_range.start_date} to {dates_range.end_date} "
                  f"with timezone_name {timezone_name}")

    if timezone_name is None:
        timezone_name = datetime_processing_params.get("default_timezone")

    predicted_boiler_t_df = boiler_t_predictor.get_need_boiler_temp(dates_range.start_date, dates_range.end_date)

    work_timezone = gettz(timezone_name)
    response_datetime_pattern = datetime_processing_params.get("response_pattern")
    predicted_boiler_t_ds = []
    for _, row in predicted_boiler_t_df.iterrows():
        datetime_ = row[column_names.TIMESTAMP]
        datetime_ = datetime_.astimezone(work_timezone)
        datetime_as_str = datetime_.strftime(response_datetime_pattern)

        boiler_t = row[column_names.TEMP_PREDICTION_BOILER_OUT_TEMP]
        boiler_t = round(boiler_t, 1)

        predicted_boiler_t_ds.append((datetime_as_str, boiler_t))

    return predicted_boiler_t_ds
