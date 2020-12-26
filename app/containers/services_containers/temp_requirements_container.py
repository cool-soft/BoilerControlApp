from dependency_injector import containers, providers

from services.temp_requirements_service.simple_temp_requirements_service import SimpleTempRequirementsService


class TempRequirementsContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    temp_graph_service = providers.Dependency()
    weather_service = providers.Dependency()

    temp_requirements_service = providers.Singleton(
        SimpleTempRequirementsService,
        temp_graph_service=temp_graph_service,
        weather_service=weather_service
    )
