import argparse

import uvicorn
from updater.updater_service.sync_updater_service import SyncUpdaterService

from backend.containers.application import Application
from backend.logging import logger
from backend.web import api_v1, api_v2, api_v3


def wire(application_container):
    application_container.core.wire(modules=(api_v1, api_v2, api_v3))
    application_container.services.wire(modules=(api_v1, api_v2, api_v3))


def main(cmd_args):
    application = Application()
    application.config.from_yaml(cmd_args.config)

    application.core.init_resources()

    # Must be placed after core.init_resources()
    logger.info("Wiring")
    wire(application)

    logger.info("Starting updater service")
    updater_service: SyncUpdaterService = application.services.updater_pkg.updater_service()
    updater_service.start_service()

    server: uvicorn.Server = application.wsgi.server()
    logger.info(f"Starting server at {server.config.host}:{server.config.port}")
    server.run(sockets=None)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Control boiler')
    parser.add_argument('--config', default="../storage/config/config.yaml", help='path to config file')
    args = parser.parse_args()
    main(args)
