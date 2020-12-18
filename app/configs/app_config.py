import yaml
from pydantic import BaseModel

from configs.boiler_t_predictor_config import BoilerTPredictorConfig
from configs.datetime_processing_config import DatetimeProcessingConfig
from configs.logging_config import LoggingConfig
from configs.service_config import ServiceConfig


class AppConfig(BaseModel):

    boiler_t_predictor: BoilerTPredictorConfig = BoilerTPredictorConfig()
    logging: LoggingConfig = LoggingConfig()
    datetime_processing: DatetimeProcessingConfig = DatetimeProcessingConfig()
    service: ServiceConfig = ServiceConfig()

    @classmethod
    def load_app_config(cls, filepath):
        with open(filepath) as f:
            config_as_dict = yaml.safe_load(f)
        app_config = cls.parse_obj(config_as_dict)
        return app_config

    def save_app_config(self, filepath):
        config_as_dict = self.dict()
        with open(filepath, "w") as f:
            yaml.safe_dump(config_as_dict, f)


class GlobalAppConfig(AppConfig):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance
