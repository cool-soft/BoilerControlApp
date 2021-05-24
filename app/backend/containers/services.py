from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Container, Dependency

from .services_containers.control_action_container import ControlActionContainer
from .services_containers.dynamic_settings_container import DynamicSettingsContainer
from .services_containers.temp_graph_container import TempGraphContainer
from .services_containers.updater_container import UpdateContainer
from .services_containers.weather_forecast_container import WeatherForecastContainer


class Services(DeclarativeContainer):
    config = Configuration(strict=True)

    settings_repository = Dependency()
    temp_graph_repository = Dependency()
    weather_forecast_repository = Dependency()
    control_actions_repository = Dependency()

    dynamic_settings_pkg = Container(
        DynamicSettingsContainer,
        config=config.dynamic_settings,
        settings_repository=settings_repository
    )
    temp_graph_pkg = Container(
        TempGraphContainer,
        temp_graph_repository=temp_graph_repository
    )
    weather_forecast_pkg = Container(
        WeatherForecastContainer,
        config=config.weather_forecast_loader,
        weather_forecast_repository=weather_forecast_repository
    )
    control_action_pkg = Container(
        ControlActionContainer,
        config=config.control_action_predictor,
        temp_graph_repository=temp_graph_repository,
        weather_forecast_repository=weather_forecast_repository,
        control_actions_repository=control_actions_repository
    )
    updater_pkg = Container(
        UpdateContainer,
        config=config.updater,
        control_actions_predictor=control_action_pkg.temp_prediction_service,
        temp_graph_updater=temp_graph_pkg.temp_graph_update_service,
        weather_forecast_updater=weather_forecast_pkg.weather_forecast_service
    )
