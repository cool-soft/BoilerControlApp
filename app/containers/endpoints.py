from dependency_injector import containers, providers


class Endpoints(containers.DeclarativeContainer):
    config = providers.Configuration()