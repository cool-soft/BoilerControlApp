
import sqlite3

import modules.config as config

cfg = config.GeneralConfig()
cfg.load()

conn = sqlite3.connect(cfg.statistic_db_path)
cursor = conn.cursor()

cursor.execute(
    """
    CREATE TABLE control_boiler_t
        (
            boiler_id UNSIGNED, 
            boiler_subid UNSIGNED,
            boiler_t UNSIGNED,
            timestamp DATETIME
        )
    """
)
conn.commit()
