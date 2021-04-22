import logging

from dependency_injector import resources
from fastapi import FastAPI


class FastAPIApp(resources.Resource):

    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of Resource")

    def init(self, api_routers: list) -> FastAPI:
        self._logger.debug("Initialization of FastAPI app")

        app = FastAPI()
        for router in api_routers:
            app.include_router(router)

        return app

    def shutdown(self, app: FastAPI) -> None:
        pass
