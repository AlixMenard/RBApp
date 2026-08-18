import sqlite3

def save_or_update_user(discord_user):
    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO users (discord_id, username, global_name, nickname, avatar)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(discord_id) DO UPDATE SET
            username = excluded.username,
            global_name = excluded.global_name,
            avatar = excluded.avatar
    """,
        (
            discord_user["id"],
            discord_user["username"],
            discord_user.get("global_name", ""),
            discord_user.get("global_name", ""),
            discord_user.get("avatar", ""),
        ),
    )
    conn.commit()
    conn.close()

def get_avatar(discord_id: str):
    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()

    # Create users table
    cursor.execute(
        """
        SELECT avatar
        FROM users
        WHERE discord_id = (?)
    """,
    (discord_id,)
    )
    avatar_hash = cursor.fetchone()[0]

    conn.commit()
    conn.close()

    return get_avatar_url(discord_id, avatar_hash)

def get_id(discord_id: str):
    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()

    # Create users table
    cursor.execute(
        """
        SELECT id
        FROM users
        WHERE discord_id = (?)
    """,
    (discord_id,)
    )
    user_id = cursor.fetchone()[0]

    conn.commit()
    conn.close()

    return user_id

def get_discord_id(user_id: str):
    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()

    # Create users table
    cursor.execute(
        """
        SELECT discord_id
        FROM users
        WHERE id = (?)
    """,
    (user_id,)
    )
    discord_id = cursor.fetchone()[0]

    conn.commit()
    conn.close()

    return discord_id

def get_avatar_url(discord_id: str, avatar_hash: str) -> str:
    if avatar_hash:
        extension = "gif" if avatar_hash.startswith("a_") else "png"
        return f"https://cdn.discordapp.com/avatars/{discord_id}/{avatar_hash}.{extension}"
    
    default_avatar_index = (int(discord_id) >> 22) % 6
    return f"https://cdn.discordapp.com/embed/avatars/{default_avatar_index}.png"