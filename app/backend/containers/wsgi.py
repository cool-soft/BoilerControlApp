# noinspection SpellCheckingInspection
import uvicorn
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Object, Resource, Singleton, Factory

from backend.resources.fastapi_app import FastAPIApp
from backend.web import api_v1, api_v2, api_v3


class WSGI(DeclarativeContainer):
    config = Configuration(strict=True)

    app = Resource(
        FastAPIApp,
        api_routers=Object([
            api_v1.api_router,
            api_v2.api_router,
            api_v3.api_router
        ])
    )

    server = Singleton(
        uvicorn.Server,
        config=Factory(
            uvicorn.Config,
            app=app,
            host=config.host,
            port=config.port,
            # log_config=None
        )
    )
