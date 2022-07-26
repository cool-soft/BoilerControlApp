from dependency_injector.resources import Resource
from dynamic_settings.repository.db_settings_repository.setting_model import Setting
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from backend.logging import logger


class SettingsDBEngine(Resource):

    def init(self, db_url: str) -> Engine:
        logger.debug(f"Initialize db engine with url: {db_url}")

        db_engine = create_engine(db_url)
        with db_engine.begin() as conn:
            Setting.metadata.create_all(conn)
        return db_engine

    def shutdown(self, db_engine: Engine) -> None:
        pass
