from dependency_injector import containers, providers


class Core(containers.DeclarativeContainer):
    config = providers.Configuration()
