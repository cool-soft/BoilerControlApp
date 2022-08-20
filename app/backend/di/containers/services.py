from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Container, Dependency

from backend.di.containers.services_containers.control_action_service_container import ControlActionServiceContainer
from backend.di.containers.services_containers.dynamic_settings_service_container import DynamicSettingsServiceContainer
from backend.di.containers.services_containers.updater_container import UpdateContainer


class Services(DeclarativeContainer):
    config = Configuration(strict=True)

    db_session_provider = Dependency()
    temp_requirements_provider = Dependency()
    control_action_repository = Dependency()
    model_parameters = Dependency()
    control_action_predictor = Dependency()
    dynamic_settings_repository = Dependency()
    keychain_repository = Dependency()

    dynamic_settings_pkg = Container(
        DynamicSettingsServiceContainer,
        db_session_provider=db_session_provider,
        settings_repository=dynamic_settings_repository
    )
    control_action_pkg = Container(
        ControlActionServiceContainer,
        config=config.control_action,
        db_session_provider=db_session_provider,
        temp_requirements_provider=temp_requirements_provider,
        control_action_repository=control_action_repository,
        model_parameters=model_parameters,
        control_action_predictor=control_action_predictor,
    )
    updater_pkg = Container(
        UpdateContainer,
        config=config.updater,
        control_action_predictor_service=control_action_pkg.control_action_prediction_service,
        control_action_service=control_action_pkg.control_action_service,
        db_session_provider=db_session_provider,
        keychain_repository=keychain_repository
    )
