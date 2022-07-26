from dependency_injector import resources
from fastapi import FastAPI

from backend.logging import logger


class FastAPIApp(resources.Resource):

    def init(self, api_routers: list) -> FastAPI:
        logger.debug("Initialization of FastAPI app")

        app = FastAPI()
        for router in api_routers:
            app.include_router(router)

        return app

    def shutdown(self, app: FastAPI) -> None:
        pass
