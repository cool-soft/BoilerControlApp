from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Dependency, Configuration, Factory

from backend.services.control_action_report_service import ControlActionReportService


class ControlActionReportContainer(DeclarativeContainer):
    config = Configuration(strict=True)

    control_action_repository = Dependency()

    control_action_report_service = Factory(
        ControlActionReportService,
        control_action_repository=control_action_repository
    )
