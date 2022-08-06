from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Container

from backend.di.containers.core import Core
from backend.di.containers.gateways import Gateways
from backend.di.containers.services import Services
from backend.di.containers.wsgi import WSGI


class Application(DeclarativeContainer):
    config = Configuration(strict=True)

    core = Container(
        Core,
        config=config.core
    )
    gateways = Container(
        Gateways,
        config=config.gateways
    )
    services = Container(
        Services,
        config=config.services,
        db_session_provider=gateways.session_factory,
    )

    wsgi = Container(
        WSGI,
        config=config.server
    )
