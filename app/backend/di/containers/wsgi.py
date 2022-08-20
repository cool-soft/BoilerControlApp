# noinspection SpellCheckingInspection
import uvicorn
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Object, Resource, Singleton, Factory

from backend.di.resources.fastapi_app import fastapi_app
from backend.controllers import api


class WSGI(DeclarativeContainer):
    config = Configuration(strict=True)

    app = Resource(
        fastapi_app,
        api_routers=Object([
            api.api_router,
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
