import os

import database.creation.users as users
import database.creation.communities as communities
import database.creation.cards as cards
import database.creation.trades as trades

import secrets
from dotenv import set_key

def rotate_secret_key(env_path: str = ".env") -> str:
    new_key = secrets.token_hex(32)
    set_key(env_path, "SECRET_KEY", new_key)
    return new_key

def reset(db_path: str):
    if os.path.exists(db_path):
        os.remove(db_path)
    f = open(db_path, "w")
    f.close()

    rotate_secret_key()

    users.init_users()

    communities.init_communities()
    communities.init_membership()

    trades.init_trades()

    cards.init_cards()