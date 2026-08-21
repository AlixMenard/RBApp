from SQL.tables import delete_table
from database.creation.trades import init_matches
import sqlite3

def update_matches(matches: list):
    delete_table("matches")
    init_matches()

    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()

    for match in matches:
        cursor.executemany("INSERT INTO matches VALUES (?, ?, ?, ?, ?)", match)

    conn.commit()
    conn.close()