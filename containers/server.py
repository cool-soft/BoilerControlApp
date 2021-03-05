import fastapi
from dependency_injector import containers, providers
# noinspection SpellCheckingInspection
from uvicorn import Config as UvicornConfig, Server as UvicornServer


class Server(containers.DeclarativeContainer):
    config = providers.Configuration()

    app = providers.Dependency()

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
