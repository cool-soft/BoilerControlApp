from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Container

from backend.containers.core import Core
from backend.containers.gateways import Gateways
from backend.containers.repositories import Repositories
from backend.containers.services import Services
from backend.containers.wsgi import WSGI


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
