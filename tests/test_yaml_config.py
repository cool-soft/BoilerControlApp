from configs import GlobalAppConfig

if __name__ == '__main__':
    cfg1 = GlobalAppConfig()
    cfg2 = GlobalAppConfig.load_app_config()
    print(cfg1 is cfg2)
    cfg1.logging.path = "../logs/log1.log"
    print(cfg1.logging.path)
    print(cfg2.logging.path)
    # cfg2.save_app_config()
