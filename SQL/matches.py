from SQL.tables import delete_table
import sqlite3

def update_matches(matches: list):
    delete_table("matches")

    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()

    for match in matches:
        cursor.executemany("INSERT INTO matches VALUES (?, ?, ?, ?, ?)", match)

    conn.commit()
    conn.close()