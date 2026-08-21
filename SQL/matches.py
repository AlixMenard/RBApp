from SQL.tables import delete_table
from database.creation.trades import init_matches
import sqlite3

def update_matches(matches: list):
    delete_table("matches")
    init_matches()

    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()

    for match in matches:
        card_id, giver_id, receiver_id, quantity, money, trade = match
        for el in match:
            print(type(el), el)
        cursor.executemany(
            """INSERT INTO matches (card_id, giver_id, receiver_id, quantity, money, trade)
            VALUES (?, ?, ?, ?, ?, ?)""",
                           (card_id, giver_id, receiver_id, quantity, money, trade,)
            )

    conn.commit()
    conn.close()