import os

import database.creation.users as users
import database.creation.communities as communities
import database.creation.cards as cards
import database.creation.trades as trades

def reset(db_path: str):
    if os.path.exists(db_path):
        os.remove(db_path)
    f = open(db_path, "w")
    f.close()

    users.init_users()

    communities.init_communities()
    communities.init_membership()

    trades.init_trades()

    cards.init_cards()