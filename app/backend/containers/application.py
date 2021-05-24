from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Container

from backend.containers.core import Core
from backend.containers.repositories import Repositories
from backend.containers.services import Services
from backend.containers.wsgi import WSGI


class Application(DeclarativeContainer):
    config = Configuration()

    repositories = Container(
        Repositories,
        config=config.reposirories
    )

    services = Container(
        Services,
        config=config.services,
        settings_repository=repositories.settings_repository,
        temp_graph_repository=repositories.temp_graph_repository,
        weather_forecast_repository=repositories.weather_forecast_repository,
        control_actions_repository=repositories.control_actions_repository
    )

    core = Container(
        Core,
        config=config.core
    )

    wsgi = Container(
        WSGI,
        config=config.server
    )
