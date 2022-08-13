from updater.updater_service.sync_updater_service import SyncUpdaterService

from backend.controllers import api_v1, api_v2, api_v3, dependencies
from backend.di.containers.application import Application


def wire(application_container):
    application_container.services.wire(modules=(api_v1, api_v2, api_v3))
    application_container.core.wire(modules=(api_v1, api_v2, api_v3, dependencies))


if __name__ == '__main__':
    application = Application()
    application.config.from_yaml("..\\storage\\configs\\dev_config.yaml")

    application.core.init_resources()
    application.database.init_resources()
    # Must be placed after core.init_resources()
    wire(application)

    application.repositories.settings_converter()

    application.control_action_predictor_pkg.dynamic_settings_repository()
    application.control_action_predictor_pkg.control_action_predictor()
    application.services.control_action_pkg.control_action_predictor()
    application.services.control_action_pkg.control_action_prediction_service()
