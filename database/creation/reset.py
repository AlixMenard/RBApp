import os
import users
import communities

def reset(db_path: str):
    if os.path.exists(db_path):
        os.remove(db_path)

    users.init_users()

    communities.init_communities()
    communities.init_membership()