import sqlite3

def init_trades():
    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS trades_out (
            card_id TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            sell BOOLEAN NOT NULL,
            trade BOOLEAN NOT NULL,
            PRIMARY KEY (card_id, user_id)
        )
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS trades_in
        (
            card_id  TEXT    NOT NULL,
            user_id  INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            buy     BOOLEAN NOT NULL,
            trade    BOOLEAN NOT NULL,
            PRIMARY KEY (card_id, user_id)
        )
        """
    )
    conn.commit()
    conn.close()

    init_matches()

def init_matches():
    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS matches
        (
            card_id  TEXT    NOT NULL,
            giver_id  INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            quantity     INTEGER NOT NULL,
            money    BOOLEAN NOT NULL,
            trade    BOOLEAN NOT NULL,
            PRIMARY KEY (card_id, giver_id, receiver_id)
        )
        """
    )

    conn.commit()
    conn.close()