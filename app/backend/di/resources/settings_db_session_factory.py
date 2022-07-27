from dependency_injector.resources import Resource
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker, Session

from backend.logging import logger


class SettingsDBSessionFactory(Resource):

    def init(self, db_engine: Engine) -> scoped_session:
        logger.debug("Initialize db session factory")
        session_factory = scoped_session(
            sessionmaker(bind=db_engine, class_=Session),
        )
        return session_factory

    def shutdown(self, session_factory: scoped_session) -> None:
        pass
