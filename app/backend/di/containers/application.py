from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Container

from backend.di.containers.core import Core
from backend.di.containers.gateways import Gateways
from backend.di.containers.repositories import Repositories
from backend.di.containers.services_containers import Services
from backend.di.containers.wsgi import WSGI


class Application(DeclarativeContainer):
    config = Configuration(strict=True)

    gateways = Container(
        Gateways,
        config=config.gateways
    )

    repositories = Container(
        Repositories,
        config=config.repositories,
        session_factory=gateways.session_factory
    )

    services = Container(
        Services,
        config=config.services,
        temp_graph_loader=gateways.temp_graph_loader,
        weather_forecast_loader=gateways.weather_forecast_loader,
        time_delta_loader=gateways.time_delta_loader,
        dynamic_settings_repository=repositories.dynamic_settings_repository,
        temp_graph_repository=repositories.temp_graph_repository,
        weather_forecast_repository=repositories.weather_forecast_repository,
        control_actions_repository=repositories.control_actions_repository,
        session_factory=gateways.session_factory
    )

    core = Container(
        Core,
        config=config.core
    )

    wsgi = Container(
        WSGI,
        config=config.server
    )
