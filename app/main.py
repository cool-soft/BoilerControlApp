import uvicorn
from fastapi import FastAPI

from containers.services import Services
from web_app import api_v1
# from web_app import api_v2

if __name__ == '__main__':
    services = Services()
    services.config.from_yaml('../config.yaml')
    # noinspection PyTypeChecker
    services.wire(modules=[api_v1])  # , api_v2])

    app = FastAPI()
    app.include_router(api_v1.api_router)
    # app.include_router(api_v2.api_router)
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=270,
        # log_config=None
    )
