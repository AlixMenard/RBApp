import sqlite3

def add_trade_out(trade_data):
    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO trades_out (card_id, user_id, quantity, sell, trade)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(card_id, user_id) DO UPDATE SET
            quantity = excluded.quantity,
            sell = excluded.sell,
            trade = excluded.trade
    """,
        trade_data
    )
    conn.commit()
    conn.close()

def add_trade_in(trade_data):
    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO trades_in (card_id, user_id, quantity, buy, trade)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(card_id, user_id) DO UPDATE SET
            quantity = excluded.quantity,
            buy = excluded.buy,
            trade = excluded.trade
    """,
        trade_data
    )
    conn.commit()
    conn.close()

def get_trades_in():
    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()
    cursor.execute("""
    SELECT t.card_id, t.user_id, t.quantity, t.buy, t.trade, 
           c.clean_name, c.image_url, 
           u.username, u.avatar, u.discord_id
    FROM trades_in t
    JOIN cards c ON t.card_id = c.id
    JOIN users u ON t.user_id = u.id
    """)
    result = cursor.fetchall()
    conn.close()
    return result

def get_trades_out():
    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()
    cursor.execute("""
    SELECT t.card_id, t.user_id, t.quantity, t.sell, t.trade, 
           c.clean_name, c.image_url, 
           u.username, u.avatar, u.discord_id
    FROM trades_out t
    JOIN cards c ON t.card_id = c.id
    JOIN users u ON t.user_id = u.id
    """)
    result = cursor.fetchall()
    conn.close()
    return result
def get_user_trades_out(user_id):
    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()
    cursor.execute("""
    SELECT t.card_id, t.quantity, t.sell, t.trade, c.clean_name, c.image_url
    FROM trades_out t
    JOIN cards c ON t.card_id = c.id
    WHERE t.user_id = ?
    """, (user_id,))
    result = cursor.fetchall()
    conn.close()
    return result

def get_user_trades_in(user_id):
    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()
    cursor.execute("""
    SELECT t.card_id, t.quantity, t.buy, t.trade, c.clean_name, c.image_url
    FROM trades_in t
    JOIN cards c ON t.card_id = c.id
    WHERE t.user_id = ?
    """, (user_id,))
    result = cursor.fetchall()
    conn.close()
    return result