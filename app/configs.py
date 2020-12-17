import os

import yaml
from pydantic import BaseModel


class BoilerTPredictorConfig(BaseModel):
    home_t_dispersion_coefficient: float = 0.97
    t_graph_path: str = "../storage/t_graph.csv"
    homes_deltas_path: str = "../storage/homes_time_delta.csv"
    optimized_t_table_path: str = "../storage/optimized_t_table.pickle"


class WeatherForecastProviderConfig(BaseModel):
    server_address: str = "https://lysva.agt.town/"
    server_timezone: str = "Asia/Yekaterinburg"
    update_interval: int = 600


class LoggingConfig(BaseModel):
    path: str = "../logs/log.log"
    level: str = "DEBUG"
    datetime_format: str = "%Y-%m-%d %H:%M:%S"
    # noinspection SpellCheckingInspection
    format: str = "[%(asctime)s] %(levelname)s - %(message)s"


class DatetimeProcessingConfig(BaseModel):
    request_datetime_patterns = [
        "(?P<year>\\d{4})-(?P<month>\\d{1,2})-(?P<day>\\d{1,2})\\s(?P<hours>\\d{1,2}):(?P<minutes>\\d{2})",
        "(?P<day>\\d{1,2})\\.(?P<month>\\d{1,2})\\.(?P<year>\\d{4})\\s(?P<hours>\\d{1,2}):(?P<minutes>\\d{2})"
    ]
    response_datetime_patterns: str = "%Y-%m-%d %H:%M"
    boiler_control_timezone: str = "Asia/Yekaterinburg"


class ServiceConfig(BaseModel):
    port: int = 270
    host: str = "0.0.0.0"


class AppConfig(BaseModel):
    __CONFIG_PATH = os.path.abspath("../config.yaml")

    boiler_t_prediction: BoilerTPredictorConfig = BoilerTPredictorConfig()
    weather_forecast_providing: WeatherForecastProviderConfig = WeatherForecastProviderConfig()
    logging: LoggingConfig = LoggingConfig()
    datetime_processing: DatetimeProcessingConfig = DatetimeProcessingConfig()
    service: ServiceConfig = ServiceConfig()

    @classmethod
    def load_app_config(cls):
        with open(cls.__CONFIG_PATH) as f:
            config_as_dict = yaml.safe_load(f)
        app_config = cls.parse_obj(config_as_dict)
        return app_config

    def save_app_config(self):
        config_as_dict = self.dict()
        with open(self.__CONFIG_PATH, "w") as f:
            yaml.safe_dump(config_as_dict, f)


class GlobalAppConfig(AppConfig):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance
