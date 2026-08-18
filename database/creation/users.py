import sqlite3


def init_users():
    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()

    # Create users table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_id TEXT UNIQUE NOT NULL,
            username TEXT NOT NULL,
            global_name TEXT,
            nickname TEXT,
            avatar TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    conn.commit()
    conn.close()
