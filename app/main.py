from containers.application import Application
from endpoints import api_v1, api_v2

if __name__ == '__main__':
    application = Application()
    application.config.from_yaml('../config.yaml')
    application.init_resources()
    application.core.wire(modules=(api_v1, api_v2))
    application.services.wire(modules=(api_v1, api_v2))

    app = application.server.fast_api_app()
    app.include_router(api_v1.api_router)
    app.include_router(api_v2.api_router)

    server = application.server.server()
    server.run()
