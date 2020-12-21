import fastapi
from dependency_injector import containers, providers
# noinspection SpellCheckingInspection
from uvicorn import Config as UvicornConfig, Server as UvicornServer


class Server(containers.DeclarativeContainer):
    config = providers.Configuration()

    fast_api_app = providers.Singleton(fastapi.FastAPI)
    server_config = providers.Singleton(
        UvicornConfig,
        app=fast_api_app,
        host=config.host,
        port=config.port,
        # log_config=None
    )
    server = providers.Singleton(
        UvicornServer,
        config=server_config
    )
