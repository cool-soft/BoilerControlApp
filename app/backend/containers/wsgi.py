from dependency_injector import containers, providers
# noinspection SpellCheckingInspection
from uvicorn import Config as UvicornConfig, Server as UvicornServer

from backend.resources.fastapi_app import FastAPIApp


class WSGI(containers.DeclarativeContainer):
    config = providers.Configuration()

    app = providers.Resource(FastAPIApp)

    server = providers.Singleton(
        UvicornServer,
        config=providers.Singleton(
            UvicornConfig,
            app=app,
            host=config.host,
            port=config.port,
            log_config=None
        )
    )
