import logging
import os

import uvicorn
from fastapi import FastAPI

from boiler_t_prediction.boiler_t_predictor import BoilerTPredictor
from configs.app_config import GlobalAppConfig
from dependency_injection import add_dependency
from web_app.api_v1 import api_router as api_v1
from web_app.api_v2 import api_router as api_v2

if __name__ == '__main__':
    CONFIG_FILEPATH = os.path.abspath("../config.yaml")

    app_config = GlobalAppConfig.load_app_config(CONFIG_FILEPATH)

    logging.basicConfig(
        filename=app_config.logging.path,
        level=app_config.logging.level,
        datefmt=app_config.logging.datetime_format,
        format=app_config.logging.format
    )

    boiler_t_predictor = BoilerTPredictor.from_config(app_config.boiler_t_predictor)
    add_dependency(boiler_t_predictor)

    app = FastAPI()
    app.include_router(api_v1)
    app.include_router(api_v2)
    uvicorn.run(
        app,
        host=app_config.service.host,
        port=app_config.service.port
    )
