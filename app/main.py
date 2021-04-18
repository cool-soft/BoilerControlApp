import argparse
import logging

from fastapi import FastAPI
from updater.updater_service.updater_service import UpdaterService

from backend.containers.application import Application
from backend.web import api_v1, api_v2


def wire(application_container):
    application_container.core.wire(modules=(api_v1, api_v2))
    application_container.services.wire(modules=(api_v1, api_v2))


def init_resources(application_container):
    application_container.core.init_resources()
    application_container.services.control_action_pkg.init_resources()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Control boiler')
    parser.add_argument('--config', default="../storage/config/config.yaml", help='path to config file')
    args = parser.parse_args()

    application = Application()
    application.config.from_yaml(args.config)
    init_resources(application)

    # Must be placed after core.init_resources()
    logger = logging.getLogger(__name__)

    logger.debug("Wiring")
    wire(application)

    app: FastAPI = application.wsgi.app()

    async def start_updater():
        updater_service_future = application.services.updater_pkg.updater_service()
        updater_service: UpdaterService = await updater_service_future
        await updater_service.start_service()
    app.add_event_handler("startup", start_updater)

    server = application.wsgi.server()
    logger.debug(f"Starting server at {server.config.host}:{server.config.port}")
    server.run()
