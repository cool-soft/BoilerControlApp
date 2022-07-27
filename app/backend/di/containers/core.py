import logging.config

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Resource


# noinspection SpellCheckingInspection
class Core(DeclarativeContainer):
    config = Configuration(strict=True)

    # Для применения настроек логгирования необходимо инициализироватьь ресурс,
    # т.к. он напрямую нигде не вызывается.
    # Для инициализации необходимо вызвать core.init_resources() у экземпляра контенера.
    logging = Resource(
        logging.config.dictConfig,
        config=config.logging,
    )
