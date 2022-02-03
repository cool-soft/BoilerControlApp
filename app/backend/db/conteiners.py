from dependency_injector import containers, providers
from sqlalchemy.orm import DeclarativeMeta

from backend.db.repository import DBRepository
from backend.db.resources import DBConnect


class DBContainer(containers.DeclarativeContainer):

    config = providers.Configuration(strict=True)

    resource = providers.Resource(
        DBConnect,
        path=config.path,
        base=config.base,
    )

    db_repository = providers.Singleton(
        DBRepository,
        session_factory=resource,
    )


def create_db_container(path: str, base: DeclarativeMeta):
    db_container = DBContainer()
    db_params = {"path": path, "base": base}
    db_container.config.from_dict(db_params)
    return db_container
