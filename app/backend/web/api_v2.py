from datetime import datetime
from typing import List, Tuple

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from backend.containers.services import Services
from backend.logger import logger
from backend.services.control_action_report_service.control_action_report_service import ControlActionReportService
from backend.web.dependencies import InputDatetimeRange, InputTimezone

api_router = APIRouter(prefix="/api/v2")


# noinspection PyTypeChecker
@api_router.get("/getPredictedBoilerT",
                response_model=List[Tuple[datetime, float]],
                response_class=JSONResponse,
                deprecated=True)
@inject
async def get_predicted_boiler_temp(
        datetime_range: InputDatetimeRange = Depends(),
        work_timezone: InputTimezone = Depends(),
        control_action_report_service: ControlActionReportService = Depends(
            Provide[Services.control_action_report_pkg.control_action_report_service]
        )
):
    # noinspection SpellCheckingInspection
    """
        Метод для получения рекомендуемой температуры, которую необходимо выставить на бойлере.
        Принимает 3 **опциональных** параметра.
        - **start_datetime**: Дата время начала управляющего воздействия в формате ISO 8601.
        - **end_datetime**: Дата время окончания управляющего воздействия в формате ISO 8601.
        - **timezone**: Имя временной зоны для обработки запроса и генерации ответа.
        Если не указан - используется временная зона из конфигов.

        ISO 8601: https://en.wikipedia.org/wiki/ISO_8601

        Временные зоны: см. «TZ database name» https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List

        ---
        Формат времени в запросе:
        - YYYY-MM-DD?HH:MM[:SS[.fffffff]][+HH:MM] где ? это T или символ пробела.

        Примеры:
        - 2020-01-30T00:17:01.1234567+05:00 - Для обработки даты и времени используется временная зона из самой строки,
        формат «O» в C#.
        - 2020-01-30 00:17:07+05:00 - Для обработки даты и времени используется временная зона из самой строки.
        - 2020-01-30 00:17+05:30 - Для обработки даты и времени используется временная зона из самой строки.
        - 2020-01-30 00:17+05 - Для обработки даты и времени используется временная зона из самой строки.
        - 2020-01-30 00:17 - Используется временная зона из параметра timezone.

        ---
        Формат времени в ответе:
        - 2020-01-30T00:17:07+05:00 - Парсится при помощи DateTimeStyle.RoundtripKind в C#.
        При формировании ответа используется врменная зона из парметра timezone.
        """

    logger.debug(f"Requested predicted boiler temp for dates range "
                 f"from {datetime_range.start_datetime} to {datetime_range.end_datetime} "
                 f"with timezone {work_timezone.name}")

    control_action = await control_action_report_service.report_v2(
        datetime_range.start_datetime,
        datetime_range.end_datetime,
        work_timezone.timezone
    )
    return control_action
