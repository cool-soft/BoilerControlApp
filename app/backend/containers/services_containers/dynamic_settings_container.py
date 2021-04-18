from dependency_injector import containers, providers
from dynamic_settings.di_service.async_dynamic_settings_di_service import AsyncDynamicSettingsDIService

from backend.resources.async_settings_db_engine import AsyncSettingsDBEngine
from backend.resources.async_settings_db_session_factory import AsyncSettingsDBSessionFactory
from backend.resources.async_settings_repository import AsyncSettingsRepository
from backend.resources.dynamic_settings_rwlock import DynamicConfigRWLock


class DynamicSettingsContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    dynamic_config = providers.Configuration()
    dynamic_config_rwlock = providers.Resource(DynamicConfigRWLock)

    db_engine = providers.Resource(AsyncSettingsDBEngine,
                                   db_url=config.db_url)
    session_factory = providers.Resource(AsyncSettingsDBSessionFactory,
                                         db_engine=db_engine)
    settings_repository = providers.Resource(AsyncSettingsRepository,
                                             session_factory=session_factory)

    settings_service = providers.Singleton(AsyncDynamicSettingsDIService,
                                           settings_repository=settings_repository,
                                           configuration=dynamic_config.provider,
                                           configuration_lock=dynamic_config_rwlock)
