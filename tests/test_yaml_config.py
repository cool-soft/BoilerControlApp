from configs import GlobalAppConfig

if __name__ == '__main__':
    cfg1 = GlobalAppConfig()
    cfg2 = GlobalAppConfig.load_app_config()
    print(cfg1 is cfg2)
    cfg2.save_app_config()
