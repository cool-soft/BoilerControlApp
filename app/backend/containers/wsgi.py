from dependency_injector import containers, providers
# noinspection SpellCheckingInspection
import uvicorn

from backend.resources.fastapi_app import FastAPIApp
from backend.web import api_v1, api_v2


class WSGI(containers.DeclarativeContainer):
    config = providers.Configuration()

    routers = providers.Object([
        api_v1.api_router,
        api_v2.api_router
    ])

    app = providers.Resource(
        FastAPIApp,
        api_routers=routers
    )

    server_config = providers.Singleton(
        uvicorn.Config,
        app=app,
        host=config.host,
        port=config.port,
        log_config=None
    )

    server = providers.Singleton(
        uvicorn.Server,
        config=server_config
    )
