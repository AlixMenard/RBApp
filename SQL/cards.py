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
                set_name, image_url, artist, alt, ovn, signed, price)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
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
    return search_cards({})

def get_sets():
    with sqlite3.connect('database/app.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT set_name FROM cards ORDER BY set_name ASC")
        sets = [row[0] for row in cursor.fetchall()]
    return sets

def search_cards(query):
    text = query.get("q")
    domains = query.getlist("domains") if hasattr(query, "getlist") else []
    types = query.getlist("type") if hasattr(query, "getlist") else []
    sets = query.getlist("sets") if hasattr(query, "getlist") else []
    alt = query.get("alt") == "true"
    ovn = query.get("ovn") == "true"
    signed = query.get("signed") == "true"

    with sqlite3.connect('database/app.db') as conn:
        cursor = conn.cursor()
        
        conditions = []
        params = []
        
        if text:
            conditions.append("(c.name LIKE ? OR c.clean_name LIKE ? OR c.id IN (SELECT card_id FROM card_tags ct2 JOIN tags t2 ON ct2.tag_id = t2.id WHERE t2.name LIKE ?))")
            params.extend([f"%{text}%", f"%{text}%", f"%{text}%"])
            
        if domains:
            placeholders = ",".join(["?"] * len(domains))
            conditions.append(f"(c.domain1 IN ({placeholders}) OR c.domain2 IN ({placeholders}))")
            params.extend(domains + domains)
            
        if types:
            placeholders = ",".join(["?"] * len(types))
            conditions.append(f"c.type IN ({placeholders})")
            params.extend(types)

        if sets:
            placeholders = ",".join(["?"] * len(sets))
            conditions.append(f"c.set_name IN ({placeholders})")
            params.extend(sets)
            
        if alt:
            conditions.append("c.alt = 1")
        if ovn:
            conditions.append("c.ovn = 1")
        if signed:
            conditions.append("c.signed = 1")
            
        sql = """
            SELECT c.id, c.name, c.clean_name, c.rarity, c.image_url, 
                   c.domain1, c.domain2, c.alt, c.ovn, c.signed,
                   GROUP_CONCAT(DISTINCT t.name) as tags, c.price, c.set_name
            FROM cards c
            LEFT JOIN card_tags ct ON c.id = ct.card_id
            LEFT JOIN tags t ON ct.tag_id = t.id
        """
        
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
            
        sql += " GROUP BY c.id ORDER BY c.name ASC LIMIT 100"
        
        cursor.execute(sql, params)
        cards = cursor.fetchall()
    return cards