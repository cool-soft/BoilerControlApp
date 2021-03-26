from dependency_injector import containers, providers

from backend.containers.core import Core
from backend.containers.services import Services
from backend.containers.server import Server


class Application(containers.DeclarativeContainer):
    config = providers.Configuration()

    services = providers.Container(
        Services,
        config=config.services
    )

    core = providers.Container(
        Core,
        config=config.core
    )

    server = providers.Container(
        Server,
        config=config.server
    )
