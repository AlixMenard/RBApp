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
    SELECT card_id, user_id, quantity, buy, trade
    FROM trades_in
                   """)
    result = cursor.fetchall()
    conn.close()
    return result

def get_trades_out():
    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()
    cursor.execute("""
    SELECT card_id, user_id, quantity, sell, trade
    FROM trades_out
                   """)
    result = cursor.fetchall()
    conn.close()
    return result