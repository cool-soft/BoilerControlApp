import argparse
import asyncio
import logging

import uvicorn
from updater.updater_service.abstract_updater_service import AbstractUpdaterService

from backend.containers.application import Application
from backend.web import api_v1, api_v2


def wire(application_container):
    application_container.core.wire(modules=(api_v1, api_v2))
    application_container.services.wire(modules=(api_v1, api_v2))


async def main(cmd_args):
    application = Application()
    application.config.from_yaml(cmd_args.config)

    application.core.init_resources()
    # Must be placed after core.init_resources()
    logger = logging.getLogger(__name__)

    logger.info("Wiring")
    wire(application)

    logger.info(f"Starting updater service")
    updater_service: AbstractUpdaterService = application.services.updater_pkg.updater_service()
    await updater_service.start_service()

    server: uvicorn.Server = application.wsgi.server()
    logger.info(f"Starting server at {server.config.host}:{server.config.port}")
    await server.serve(sockets=None)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Control boiler')
    parser.add_argument('--config', default="../storage/config/config.yaml", help='path to config file')
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    loop.run_until_complete(main(args))
