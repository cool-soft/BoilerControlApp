from dynamic_settings.repository.db_settings_repository.setting_model import Setting
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker, Session
from updater_keychain.keychain_db_repository import Keychain

from backend.models.db import ControlAction, TempGraph


def db_session_factory(cache_db_engine: Engine,
                       settings_db_engine: Engine
                       ) -> scoped_session:
    return scoped_session(
        sessionmaker(
            class_=Session,
            binds={
                ControlAction: cache_db_engine,
                TempGraph: cache_db_engine,
                Keychain: cache_db_engine,
                Setting: settings_db_engine
            }
        ),
    )


def cache_database(cache_db_engine: Engine) -> None:
    with cache_db_engine.begin() as conn:
        ControlAction.metadata.create_all(conn)
        TempGraph.metadata.create_all(conn)


def settings_database(settings_db_engine: Engine) -> None:
    with settings_db_engine.begin() as conn:
        Setting.metadata.create_all(conn)
