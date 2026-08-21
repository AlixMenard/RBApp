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
        cursor.execute(
            """INSERT INTO matches (card_id, giver_id, receiver_id, quantity, money, trade)
            VALUES (?, ?, ?, ?, ?, ?)""",
                           (card_id, giver_id, receiver_id, quantity, money, trade,)
            )

    conn.commit()
    conn.close()

def get_user_matches(user_id):
    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.card_id, m.giver_id, m.receiver_id, m.quantity, m.money, m.trade,
               c.name, c.image_url,
               giver.username, giver.avatar, giver.discord_id,
               receiver.username, receiver.avatar, receiver.discord_id
        FROM matches m
        JOIN cards c ON m.card_id = c.id
        JOIN users giver ON m.giver_id = giver.id
        JOIN users receiver ON m.receiver_id = receiver.id
        WHERE m.giver_id = ? OR m.receiver_id = ?
    """, (user_id, user_id))
    result = cursor.fetchall()
    conn.close()
    return result