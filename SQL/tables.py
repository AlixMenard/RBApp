import sqlite3

def delete_table(table_name: str) -> None:
    conn = sqlite3.connect('database/app.db')
    cursor = conn.cursor()
    cursor.execute(f"DROP TABLE IF  EXISTS {table_name}")
    conn.commit()
    conn.close()