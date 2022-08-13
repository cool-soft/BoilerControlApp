from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Container

from backend.di.containers.components.control_action_predictor_container import ControlActionPredictorContainer
from backend.di.containers.components.model_container import ModelContainer
from backend.di.containers.components.temp_graph_provider_container import TempGraphProviderContainer
from backend.di.containers.components.temp_requirements_provider_container import TempRequirementsProviderContainer
from backend.di.containers.components.weather_forecast_provider_container import WeatherForecastProviderContainer
from backend.di.containers.core import Core
from backend.di.containers.database import Database
from backend.di.containers.gateways import Gateways
from backend.di.containers.repositories import Repositories
from backend.di.containers.services import Services
from backend.di.containers.wsgi import WSGI


class Application(DeclarativeContainer):
    config = Configuration(strict=True)

    core = Container(
        Core,
        config=config.core
    )
    gateways = Container(Gateways)  # TODO: proxy
    database = Container(
        Database,
        config=config.database
    )
    repositories = Container(
        Repositories,
        db_session_provider=database.db_session_provider
    )

    weather_forecast_pkg = Container(
        WeatherForecastProviderContainer,
        weather_forecast_loader=gateways.weather_forecast_loader
    )
    temp_graph_pkg = Container(
        TempGraphProviderContainer,
        config=config.temp_graph,
        db_session_provider=database.db_session_provider,
        temp_graph_loader=gateways.temp_graph_loader,
        temp_graph_cache_repository=repositories.temp_graph_cache_repository,
        keychain_repository=repositories.keychain_repository,
    )
    temp_requirements_pkg = Container(
        TempRequirementsProviderContainer,
        weather_forecast_loader=weather_forecast_pkg.weather_forecast_provider,
        temp_graph_loader=temp_graph_pkg.temp_graph_provider
    )

    model_pkg = Container(
        ModelContainer,
        config=config.model
    )

    control_action_predictor_pkg = Container(
        ControlActionPredictorContainer,
        db_session_provider=database.db_session_provider,
        dynamic_settings_repository=repositories.dynamic_settings_repository,
        heating_system_model=model_pkg.heating_system_model
    )

    services = Container(
        Services,
        config=config.services,
        db_session_provider=database.db_session_provider,
        temp_requirements_provider=temp_requirements_pkg.temp_requirements_provider,
        control_action_repository=repositories.control_action_cache_repository,
        model_requirements=model_pkg.model_requirements,
        control_action_predictor=control_action_predictor_pkg.control_action_predictor,
        dynamic_settings_repository=repositories.dynamic_settings_repository
    )

    wsgi = Container(
        WSGI,
        config=config.server
    )
