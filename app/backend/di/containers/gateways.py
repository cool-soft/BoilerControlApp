from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Resource

from backend.di.resources.database import db_session_factory


class Gateways(DeclarativeContainer):
    config = Configuration(strict=True)

    session_factory = Resource(
        db_session_factory,
        db_url=config.db_url,
        settings_db_url=config.settings_db_url
    )
