
import sqlite3

import config


if __name__ == '__main__':

    conn = sqlite3.connect(config.DB_PATH)
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
