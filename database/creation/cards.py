import sqlite3

def init_cards():
    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS cards (
            id TEXT PRIMARY KEY,
            riftbound_id TEXT,
            name TEXT NOT NULL,
            clean_name TEXT,
            energy INTEGER,
            power INTEGER,
            might INTEGER,
            type TEXT NOT NULL,
            supertype TEXT,
            rarity TEXT,
            domain1 TEXT NOT NULL,
            domain2 TEXT,
            set_id TEXT NOT NULL,
            set_name TEXT NOT NULL,
            image_url TEXT NOT NULL,
            artist TEXT NOT NULL,
            alt BOOLEAN NOT NULL,
            ovn BOOLEAN NOT NULL,
            signed BOOLEAN NOT NULL
        )
    """
    )

    conn.commit()
    conn.close()

    init_tags()


def init_tags():
    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tags
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS card_tags
        (
            card_id TEXT NOT NULL,
            tag_id INTEGER NOT NULL
        )
        """
    )

    conn.commit()
    conn.close()
