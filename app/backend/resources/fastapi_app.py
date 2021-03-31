import logging

import pandas as pd
from dependency_injector import resources
from fastapi import FastAPI

from backend.web import api_v1, api_v2


class FastAPIApp(resources.Resource):

    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of Resource")

    def init(self) -> FastAPI:
        self._logger.debug("Initialization of FastAPI app")

        app = FastAPI()
        app.include_router(api_v1.api_router)
        app.include_router(api_v2.api_router)

        return app

    def shutdown(self, temp_graph: pd.DataFrame):
        pass
