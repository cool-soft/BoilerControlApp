from dynamic_settings.repository.db_settings_repository.setting_model import Setting
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker, Session
from updater.update_datetime_memento.update_datetime_db_repository import UpdateDatetimeDBRecord

from backend.models.db import ControlActionDBModel, TempGraphDBModel


def db_session_factory(cache_db_engine: Engine,
                       settings_db_engine: Engine
                       ) -> scoped_session:
    return scoped_session(
        sessionmaker(
            class_=Session,
            binds={
                ControlActionDBModel: cache_db_engine,
                TempGraphDBModel: cache_db_engine,
                UpdateDatetimeDBRecord: cache_db_engine,
                Setting: settings_db_engine
            }
        ),
    )


def cache_database(cache_db_engine: Engine) -> None:
    with cache_db_engine.begin() as conn:
        ControlActionDBModel.metadata.create_all(conn)
        TempGraphDBModel.metadata.create_all(conn)
        UpdateDatetimeDBRecord.metadata.create_all(conn)


def settings_database(settings_db_engine: Engine) -> None:
    with settings_db_engine.begin() as conn:
        Setting.metadata.create_all(conn)
