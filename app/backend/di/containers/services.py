from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Container, Dependency

from .services.control_action_container import ControlActionContainer
from .services.control_action_report_container import ControlActionReportContainer
from .services.dynamic_settings_container import DynamicSettingsContainer
from .services.temp_graph_container import TempGraphContainer
from .services.updater_container import UpdateContainer
from .services.weather_forecast_container import WeatherForecastContainer


class Services(DeclarativeContainer):
    config = Configuration(strict=True)
    session_factory = Dependency()

    temp_graph_loader = Dependency()
    weather_forecast_loader = Dependency()

    dynamic_settings_repository = Dependency()
    temp_graph_repository = Dependency()
    time_delta_loader = Dependency()
    weather_forecast_repository = Dependency()
    control_actions_repository = Dependency()

    dynamic_settings_pkg = Container(
        DynamicSettingsContainer,
        config=config.dynamic_settings,
        settings_repository=dynamic_settings_repository,
        session_factory=session_factory
    )
    temp_graph_pkg = Container(
        TempGraphContainer,
        temp_graph_loader=temp_graph_loader,
        temp_graph_repository=temp_graph_repository
    )
    weather_forecast_pkg = Container(
        WeatherForecastContainer,
        weather_forecast_loader=weather_forecast_loader,
        weather_forecast_repository=weather_forecast_repository
    )
    control_action_pkg = Container(
        ControlActionContainer,
        config=config.control_action_predictor,
        time_delta_loader=time_delta_loader,
        temp_graph_repository=temp_graph_repository,
        weather_forecast_repository=weather_forecast_repository,
        control_actions_repository=control_actions_repository,
        dynamic_settings_service=dynamic_settings_pkg.settings_service
    )
    control_action_report_pkg = Container(
        ControlActionReportContainer,
        config=config.control_action_reporter,
        control_action_repository=control_actions_repository
    )
    updater_pkg = Container(
        UpdateContainer,
        config=config.updater,
        control_actions_predictor=control_action_pkg.temp_prediction_service,
        temp_graph_updater=temp_graph_pkg.temp_graph_update_service,
        weather_forecast_updater=weather_forecast_pkg.weather_forecast_service
    )
