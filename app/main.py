import argparse
import logging

from backend.containers.application import Application
from backend.web import api_v1, api_v2


def wire(application_container):
    application_container.core.wire(modules=(api_v1, api_v2))
    application_container.services.wire(modules=(api_v1, api_v2))


def init_resources(application_container):
    application_container.core.init_resources()
    application_container.services.boiler_temp_prediction.init_resources()


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

    server = application.wsgi.server()
    logger.debug(f"Starting server at {server.config.host}:{server.config.port}")
    server.run()
