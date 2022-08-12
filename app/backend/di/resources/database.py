from copy import deepcopy
from typing import List, Dict

from dynamic_settings.repository.abstract_settings_repository import AbstractSyncSettingsRepository
from dynamic_settings.repository.db_settings_repository.dtype_converters import DTypeConverter
from dynamic_settings.repository.db_settings_repository.setting_model import Setting
from dynamic_settings.repository.db_settings_repository.settings_converter import SettingsConverter
from dynamic_settings.repository.db_settings_repository.sync_db_settings_repository import SyncDBSettingsRepository
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, Session

from backend.models.db import WeatherForecast, ControlAction, TempGraph, TempRequirements


def db_session_factory(db_url: str, settings_db_url: str) -> scoped_session:
    db_engine = create_engine(db_url)
    settings_db_engine = create_engine(settings_db_url)

    with db_engine.begin() as conn:
        WeatherForecast.metadata.create_all(conn)
        ControlAction.metadata.create_all(conn)
        TempGraph.metadata.create_all(conn)
        TempRequirements.metadata.create_all(conn)

    with settings_db_engine.begin() as conn:
        Setting.metadata.create_all(conn)

    session_factory = scoped_session(
        sessionmaker(
            class_=Session,
            binds={
                WeatherForecast: db_engine,
                ControlAction: db_engine,
                TempGraph: db_engine,
                TempRequirements: db_engine,
                Setting: settings_db_engine
            }
        ),
    )
    return session_factory


def dynamic_settings_repository(db_session_provider: scoped_session,
                                dtype_converters: List[DTypeConverter],
                                default_settings: Dict
                                ) -> AbstractSyncSettingsRepository:
    settings_converter = SettingsConverter(dtype_converters)
    settings_repository = SyncDBSettingsRepository(
        db_session_provider,
        settings_converter
    )
    with db_session_provider.begin() as session:
        current_settings = settings_repository.get_all()
        new_settings = deepcopy(default_settings)
        new_settings.update(current_settings)
        settings_repository.set_all(new_settings)
        session.commit()
    db_session_provider.remove()
    return settings_repository
