import argparse
import logging

from dependency_injector import providers
from fastapi import FastAPI

from containers.application import Application
from endpoints import api_v1, api_v2


def create_fast_api_app():
    fast_api_app = FastAPI()
    fast_api_app.include_router(api_v1.api_router)
    fast_api_app.include_router(api_v2.api_router)
    return fast_api_app


def wire(application_container):
    application_container.core.wire(modules=(api_v1, api_v2))
    application_container.services.wire(modules=(api_v1, api_v2))


def init_resources(application_container):
    application_container.core.init_resources()
    application_container.services.boiler_temp_prediction.init_resources()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Control boiler')
    parser.add_argument('--config', default="/etc/boiler_config.yaml", help='path to config file')
    args = parser.parse_args()

    application = Application()
    application.config.from_yaml(args.config)

    init_resources(application)

    logger = logging.getLogger(__name__)  # Must be placed after core.init_resources()

    logger.debug("Wiring")
    wire(application)

    logger.debug("Creating FastAPI app")
    app = create_fast_api_app()
    application.server.app.override(providers.Object(app))

    server = application.server.server()
    logger.debug(f"Starting server at {server.config.host}:{server.config.port}")
    server.run()
