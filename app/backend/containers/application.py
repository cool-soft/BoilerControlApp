from dependency_injector import containers, providers

from backend.containers.core import Core
from backend.containers.services import Services
from backend.containers.wsgi import WSGI
from backend.resources.dynamic_settings_rwlock import DynamicConfigRWLock


class Application(containers.DeclarativeContainer):
    config = providers.Configuration()
    dynamic_config = providers.Configuration()
    dynamic_config_rwlock = providers.Resource(DynamicConfigRWLock)

    services = providers.Container(
        Services,
        config=config.services,
        dynamic_config=dynamic_config,
        dynamic_config_rwlock=dynamic_config_rwlock,
    )

    core = providers.Container(
        Core,
        config=config.core
    )

    wsgi = providers.Container(
        WSGI,
        config=config.server
    )
