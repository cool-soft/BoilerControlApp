from dependency_injector import containers, providers

from containers.endpoints import Endpoints
from containers.services import Services
from containers.server import Server


class Application(containers.DeclarativeContainer):
    config = providers.Configuration()

    services = providers.Container(
        Services,
        config=config.services
    )

    endpoints = providers.Container(
        Endpoints,
        config=config.endpoints
    )

    server = providers.Container(
        Server,
        config=config.server
    )