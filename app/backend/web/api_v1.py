import logging

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from backend.containers.core import Core
from backend.containers.services import Services
from backend.repositories.control_action_cache_repository import ControlActionsCacheRepository
from backend.web.dependencies import InputDatesRange, InputTimezone
from boiler.constants import column_names

api_router = APIRouter(prefix="/api/v1")


@api_router.get("/getPredictedBoilerT", response_class=JSONResponse, deprecated=True)
@inject
async def get_predicted_boiler_t(
        dates_range: InputDatesRange = Depends(),
        work_timezone: InputTimezone = Depends(),
        control_action_repository: ControlActionsCacheRepository = Depends(
            Provide[Services.control_action_pkg.control_actions_repository]
        ),
        datetime_processing_params=Depends(Provide[Core.config.datetime_processing])
):
    """
        Метод для получения рекомендуемой температуры, которую необходимо выставить на бойлере.
        Принимает 3 **опциональных** параметра.
        - **start_datetime**: Дата время начала управляющего воздействия (формат см. в конфигах).
        - **end_datetime**: Дата время окончания управляющего воздействия (формат см. в конфигах).
        - **timezone**: Имя временной зоны для обработки запроса и генерации ответа.
        Если не указан - используется временная зона из конфигов.
    """

    _logger = logging.getLogger(__name__)
    _logger.debug(f"Requested predicted boiler temp for dates range "
                  f"from {dates_range.start_date} to {dates_range.end_date} "
                  f"with timezone {work_timezone.name}")

    boiler_control_actions_df = await control_action_repository.get_control_action(
        dates_range.start_date,
        dates_range.end_date
    )

    predicted_boiler_temp_list = []
    if not boiler_control_actions_df.empty:

        datetimes = boiler_control_actions_df[column_names.TIMESTAMP]
        datetimes = datetimes.dt.tz_convert(work_timezone.timezone)
        response_datetime_pattern = datetime_processing_params.get("response_pattern")
        datetimes = datetimes.dt.strftime(response_datetime_pattern)
        datetimes = datetimes.to_list()

        boiler_out_temps = boiler_control_actions_df[column_names.FORWARD_PIPE_COOLANT_TEMP]
        boiler_out_temps = boiler_out_temps.round(1)
        boiler_out_temps = boiler_out_temps.to_list()

        for datetime_, boiler_out_temp in zip(datetimes, boiler_out_temps):
            predicted_boiler_temp_list.append((datetime_, boiler_out_temp))

    return predicted_boiler_temp_list
