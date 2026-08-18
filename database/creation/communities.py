import sqlite3


def init_communities():
    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()

    # Create users table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS communities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            country TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    conn.commit()
    conn.close()

def init_membership():
    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()

    # Create users table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS membership (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            commu_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    conn.commit()
    conn.close()