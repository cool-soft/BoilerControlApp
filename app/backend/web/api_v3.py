from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from backend.constants import config_names
from backend.containers.services import Services
from backend.models.api.v3.setting import Setting
from backend.services.SettingsService import SettingsService

api_router = APIRouter(prefix="/api/v3")


@api_router.put("/settings/apartmentHouseMinTempCoefficient", status_code=204)
@inject
async def put_apartment_house_min_temp_coefficient(
        coefficient: float,
        settings_service: SettingsService = Depends(
            Provide[Services.dynamic_settings_pkg.settings_service]
        )
):
    await settings_service.set_setting(config_names.APARTMENT_HOUSE_MIN_TEMP_COEFFICIENT, coefficient)


@api_router.put("/settings/maxBoilerTemp", status_code=204)
@inject
async def put_max_boiler_temp(
        temp: float,
        settings_service: SettingsService = Depends(
            Provide[Services.dynamic_settings_pkg.settings_service]
        )
):
    await settings_service.set_setting(config_names.MAX_BOILER_TEMP, temp)


@api_router.put("/settings/minBoilerTemp", status_code=204)
@inject
async def put_min_boiler_temp(
        temp: float,
        settings_service: SettingsService = Depends(
            Provide[Services.dynamic_settings_pkg.settings_service]
        )
):
    await settings_service.set_setting(config_names.MIN_BOILER_TEMP, temp)


@api_router.put("/settings/putModelErrorSize", status_code=204)
@inject
async def put_model_error_size(
        value: float,
        settings_service: SettingsService = Depends(
            Provide[Services.dynamic_settings_pkg.settings_service]
        )
):
    await settings_service.set_setting(config_names.MODEL_ERROR_SIZE, value)


@api_router.get("/settings/apartmentHouseMinTempCoefficient", response_model=Setting)
@inject
async def get_apartment_house_min_temp_coefficient(
        settings_service: SettingsService = Depends(
            Provide[Services.dynamic_settings_pkg.settings_service]
        )
):
    return await settings_service.get_setting(config_names.APARTMENT_HOUSE_MIN_TEMP_COEFFICIENT)


@api_router.get("/settings/maxBoilerTemp", response_model=Setting)
@inject
async def get_max_boiler_temp(
        settings_service: SettingsService = Depends(
            Provide[Services.dynamic_settings_pkg.settings_service]
        )
):
    return await settings_service.get_setting(config_names.MAX_BOILER_TEMP)


@api_router.get("/settings/minBoilerTemp", response_model=Setting)
@inject
async def get_min_boiler_temp(
        settings_service: SettingsService = Depends(
            Provide[Services.dynamic_settings_pkg.settings_service]
        )
):
    return await settings_service.get_setting(config_names.MIN_BOILER_TEMP)


@api_router.get("/settings/modelErrorSize", response_model=Setting)
@inject
async def get_model_error_size(
        settings_service: SettingsService = Depends(
            Provide[Services.dynamic_settings_pkg.settings_service]
        )
):
    return await settings_service.get_setting(config_names.MODEL_ERROR_SIZE)


# noinspection PyTypeChecker
@api_router.get("/settings", response_model=List[Setting])
@inject
async def get_settings(
        settings_service: SettingsService = Depends(
            Provide[Services.dynamic_settings_pkg.settings_service]
        )
):
    return await settings_service.get_all_settings()
