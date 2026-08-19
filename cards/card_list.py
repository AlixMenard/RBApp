from cards.riftcodex_api import get_cards
from SQL.tables import delete_table
from SQL.cards import add_cards, add_tags
from database.creation.cards import init_cards

import re
from tqdm import tqdm


def normalize_clean_name(name):
    text = name.replace("'", "").replace(",", "")
    text = text.replace("(", "").replace(")", "")
    text = text.replace("-", " ")
    return re.sub(r"\s+", " ", text).strip()

def update_cards():

    delete_table("card_tags")
    delete_table("tags")
    delete_table("cards")
    init_cards()

    all_cards = get_cards()

    deduplicated_cards = {}
    for card in all_cards:
        rb_id = card.get("riftbound_id")
        if not rb_id:
            continue

        metadata = card.get("metadata") or {}
        is_alt = metadata.get("alternate_art") or False
        is_ovn = metadata.get("overnumbered") or False
        is_signed = metadata.get("signature") or False

        key = (rb_id, is_alt, is_ovn, is_signed)
        deduplicated_cards.setdefault(key, card)

    all_cards_clean = []
    for key in tqdm(deduplicated_cards):
        card = deduplicated_cards[key]
        if len(card["classification"]["domain"])>1:
            d1 = card["classification"]["domain"][0]
            d2 = card["classification"]["domain"][1]
        else:
            d1 = card["classification"]["domain"][0]
            d2 = None

        metadata = card.get("metadata") or {}
        attributes = card.get("attributes") or {}

        clean_name = metadata.get("clean_name") or normalize_clean_name(card["name"])

        card_clean = (card["id"], card["riftbound_id"], card["name"], clean_name,
                      attributes.get("energy") or 0, attributes.get("power") or 0,
                      attributes.get("might") or 0, card["classification"]["type"],
                      card["classification"]["supertype"], card["classification"]["rarity"],
                      d1, d2, card["set"]["set_id"], card["set"]["label"],
                      card["media"]["image_url"], card["media"]["artist"],
                      metadata.get("alternate_art") or False, (metadata.get("overnumbered") or False) or (metadata.get("signature") or False),
                      metadata.get("signature") or False,
                      0)
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