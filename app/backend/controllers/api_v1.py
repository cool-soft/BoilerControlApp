from typing import Tuple, List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from backend.di.containers.services import Services
from backend.logging import logger
from backend.services.control_action_report_service import ControlActionReportService
from backend.controllers.dependencies import InputDatesRange, InputTimezone

api_router = APIRouter(prefix="/api/v1")


# noinspection PyTypeChecker
@api_router.get("/getPredictedBoilerT",
                response_class=JSONResponse,
                response_model=List[Tuple[str, float]],
                deprecated=True)
@inject
def get_predicted_boiler_temp(
        dates_range: InputDatesRange = Depends(),
        work_timezone: InputTimezone = Depends(),
        control_action_report_service: ControlActionReportService = Depends(
            Provide[
                Services.control_action_pkg.control_action_report_service
            ]
        )
):
    """
        Метод для получения рекомендуемой температуры, которую необходимо выставить на бойлере.
        Принимает 3 **опциональных** параметра.
        - **start_datetime**: Дата время начала управляющего воздействия (формат см. в конфигах).
        - **end_datetime**: Дата время окончания управляющего воздействия (формат см. в конфигах).
        - **weather_data_timezone**: Имя временной зоны для обработки запроса и генерации ответа.
        Если не указан - используется временная зона из конфигов.
    """

    logger.debug(f"Requested predicted boiler temp for dates range "
                 f"from {dates_range.start_date} to {dates_range.end_date} "
                 f"with weather_data_timezone {work_timezone.name}")

    control_action = control_action_report_service.report_v1(
        dates_range.start_date,
        dates_range.end_date,
        work_timezone.timezone
    )
    return control_action
