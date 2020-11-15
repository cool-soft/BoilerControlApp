
import sqlite3

import config


if __name__ == '__main__':

    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()

    cursor.executescript(
        """
        CREATE TABLE control_boiler_t 
        (
            boiler_id UNSIGNED, 
            boiler_subid UNSIGNED,
            boiler_t UNSIGNED,
            timestamp TEXT
        );
        
        CREATE TABLE forecasted_weather_t
        (
            city TEXT,
            weather_t UNSIGNED,
            timestamp TEXT
        );
        """
    )
    conn.commit()
