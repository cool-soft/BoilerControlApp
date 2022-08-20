import argparse

import uvicorn
from updater.updater_service.sync_updater_service import SyncUpdaterService

from backend.di.containers.application import Application
from backend.logging import logger
from backend.controllers import api, dependencies


def wire(application_container):
    application_container.services.wire(modules=(api,))
    application_container.core.wire(modules=(api, dependencies))


def main(cmd_args):
    application = Application()
    application.config.from_yaml(cmd_args.config)

    application.core.init_resources()
    application.database.init_resources()
    # Must be placed after core.init_resources()
    wire(application)

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
