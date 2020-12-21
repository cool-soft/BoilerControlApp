from dependency_injector import containers, providers

from containers.core import Core
from containers.services import Services
from containers.server import Server


class Application(containers.DeclarativeContainer):
    config = providers.Configuration()

    services = providers.Container(
        Services,
        config=config.services
    )

    core = providers.Container(
        Core,
        config=config.endpoints
    )

    server = providers.Container(
        Server,
        config=config.server
    )