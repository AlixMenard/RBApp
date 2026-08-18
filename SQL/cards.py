import sqlite3

def add_tags(tags: list):
    with sqlite3.connect('database/app.db') as conn:
        cursor = conn.cursor()
        for tag in tags:
            cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
            conn.commit()

        cursor.execute("SELECT * FROM tags")

        tags = cursor.fetchall()
        tags_dict = {}
        for tag in tags:
            tags_dict[tag[1]] = tag[0]
    return tags_dict

def add_cards(cards: list) -> None:
    with sqlite3.connect('database/app.db') as conn:
        cursor = conn.cursor()
        for card, tags in cards:
            cursor.execute(
                """INSERT INTO cards (id, riftbound_id, name, clean_name, energy,
                power, might, type, supertype, rarity, domain1, domain2, set_id,
                set_name, image_url, artist, alt, ovn, signed)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                card
            )

            for tag in tags:
                cursor.execute("INSERT INTO card_tags (card_id, tag_id) VALUES (?,?)",
                               (card[0], tag))

            conn.commit()

def get_image(card_id: int) -> str:
    with sqlite3.connect('database/app.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT image_url FROM cards WHERE id = ?", (card_id,))
        image = cursor.fetchone()[0]
    return image

def get_cards():
    with sqlite3.connect('database/app.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, clean_name, rarity, image_url FROM cards")
        cards = cursor.fetchall()
    return cards