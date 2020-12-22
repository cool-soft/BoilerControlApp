from dependency_injector import providers
from fastapi import FastAPI

from containers.application import Application
from endpoints import api_v1, api_v2

if __name__ == '__main__':
    application = Application()

    app = FastAPI()
    app.include_router(api_v1.api_router)
    app.include_router(api_v2.api_router)
    application.server.app.override(providers.Object(app))

    application.config.from_yaml('../config.yaml')
    application.init_resources()
    
    application.core.wire(modules=(api_v1, api_v2))
    application.services.wire(modules=(api_v1, api_v2))

    server = application.server.server()
    server.run()
