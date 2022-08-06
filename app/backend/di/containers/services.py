from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Container, Dependency

from backend.di.containers.services_containers.control_action_container import ControlActionContainer
from backend.di.containers.services_containers.dynamic_settings_container import DynamicSettingsContainer
from backend.di.containers.services_containers.temp_graph_container import TempGraphContainer
from backend.di.containers.services_containers.updater_container import UpdateContainer
from backend.di.containers.services_containers.weather_forecast_container import WeatherForecastContainer


class Services(DeclarativeContainer):
    config = Configuration(strict=True)
    db_session_provider = Dependency()

    dynamic_settings_pkg = Container(
        DynamicSettingsContainer,
        dynamic_settings_db_session_provider=db_session_provider
    )
    temp_graph_pkg = Container(
        TempGraphContainer,
        db_session_provider=db_session_provider
    )
    weather_forecast_pkg = Container(
        WeatherForecastContainer,
        db_session_provider=db_session_provider
    )
    control_action_pkg = Container(
        ControlActionContainer,
        config=config.control_action,
        db_session_provider=db_session_provider,
        temp_graph_repository=temp_graph_pkg.temp_graph_repository,
        weather_forecast_repository=weather_forecast_pkg.weather_forecast_repository,
        dynamic_settings_service=dynamic_settings_pkg.settings_service
    )
    updater_pkg = Container(
        UpdateContainer,
        config=config.updater,
        control_actions_predictor=control_action_pkg.control_action_prediction_service,
        temp_graph_updater=temp_graph_pkg.temp_graph_update_service,
        weather_forecast_updater=weather_forecast_pkg.weather_forecast_update_service
    )
