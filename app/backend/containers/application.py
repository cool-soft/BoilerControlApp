from dependency_injector import containers, providers

from backend.containers.core import Core
from backend.containers.services import Services
from backend.containers.wsgi import WSGI


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

    wsgi = providers.Container(
        WSGI,
        config=config.server
    )
