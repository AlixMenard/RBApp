from cards.riftcodex_api import get_cards
from SQL.tables import delete_table
from SQL.cards import add_cards, add_tags
from database.creation.cards import init_cards

from tqdm import tqdm

def update_cards():

    delete_table("cards")
    init_cards()

    all_cards = get_cards()

    all_cards_clean = []
    for card in tqdm(all_cards):
        if len(card["classification"]["domain"])>1:
            d1 = card["classification"]["domain"][0]
            d2 = card["classification"]["domain"][1]
        else:
            d1 = card["classification"]["domain"][0]
            d2 = None

        card_clean = (card["id"], card["riftbound_id"], card["name"], card["metadata"].get("clean_name",card["name"]),
                      card["attributes"].get("energy", 0), card["attributes"].get("power", 0),
                      card["attributes"].get("might", 0), card["classification"]["type"],
                      card["classification"]["supertype"], card["classification"]["rarity"],
                      d1, d2, card["set"]["set_id"], card["set"]["label"],
                      card["media"]["image_url"], card["media"]["artist"],
                      card["metadata"]["alternate_art"], card["metadata"]["overnumbered"],
                      card["metadata"]["signature"])
        tags = card["tags"]

        all_cards_clean.append((card_clean, tags))

    all_tags = set()
    for _, tags in all_cards_clean:
        all_tags.update(tags)
    all_tags = sorted(list(all_tags))

    tags_dict = add_tags(all_tags)
    for i in range(len(all_cards_clean)):
        card, tags = all_cards_clean[i]

        tags = [tags_dict[t] for t in tags]

        all_cards_clean[i] = (card, tags)

    add_cards(all_cards_clean)