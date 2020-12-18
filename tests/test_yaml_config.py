from configs.app_config import GlobalAppConfig

if __name__ == '__main__':
    cfg1 = GlobalAppConfig()
    cfg2 = GlobalAppConfig.load_app_config("../config.yaml")
    print(cfg1 is cfg2)
    cfg1.logging.level = "INFO"
    print(cfg2.logging.level == "INFO")
