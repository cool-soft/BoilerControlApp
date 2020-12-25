from dependency_injector import containers, providers
import logging.config


class Core(containers.DeclarativeContainer):
    config = providers.Configuration()

    # Для применения настроек логгирования необходимо инициализироватьь ресурс,
    # т.к. он напрямую нигде не вызывается.
    # Для инициализации необходимо вызвать core.init_resources() у экземпляра контенера.
    logging = providers.Resource(
        logging.config.dictConfig,
        config=config.logging,
    )
