from fastapi import FastAPI


def fastapi_app(api_routers: list) -> FastAPI:
    app = FastAPI()
    for router in api_routers:
        app.include_router(router)
    return app
