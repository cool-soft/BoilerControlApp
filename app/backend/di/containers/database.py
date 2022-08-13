from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Callable, Resource
from sqlalchemy import create_engine

from backend.di.resources.database import db_session_factory, cache_database, settings_database

# TODO: init resources
class Database(DeclarativeContainer):
    config = Configuration(strict=True)

    cache_db_engine = Callable(
        create_engine,
        config.cache_db_url
    )
    settings_db_engine = Callable(
        create_engine,
        config.settings_db_url
    )
    db_session_provider = Resource(
        db_session_factory,
        cache_db_engine=cache_db_engine,
        settings_db_engine=settings_db_engine
    )

    cache_database = Resource(cache_database, cache_db_engine)
    settings_database = Resource(settings_database, settings_db_engine)
