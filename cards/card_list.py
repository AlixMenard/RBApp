from cards.riftcodex_api import get_cards
from SQL.tables import delete_table
from SQL.cards import add_cards, add_tags
from database.creation.cards import init_cards

from tqdm import tqdm

def update_cards():

    delete_table("card_tags")
    delete_table("tags")
    delete_table("cards")
    init_cards()

    all_cards = get_cards()

    # Deduplicate by riftbound_id, prioritizing standard versions
    deduplicated_cards = {}
    for card in all_cards:
        rb_id = card.get("riftbound_id")
        if not rb_id:
            continue

        metadata = card.get("metadata") or {}
        is_alt = metadata.get("alternate_art") or False
        is_ovn = metadata.get("overnumbered") or False
        is_signed = metadata.get("signature") or False

        # Priority: prefer regular cards (not alt, not ovn, not signed)
        priority = (not is_alt, not is_ovn, not is_signed)

        if rb_id not in deduplicated_cards:
            deduplicated_cards[rb_id] = (card, priority)
        else:
            _, existing_priority = deduplicated_cards[rb_id]
            if priority > existing_priority:
                deduplicated_cards[rb_id] = (card, priority)

    all_cards_clean = []
    for rb_id in tqdm(deduplicated_cards):
        card, _ = deduplicated_cards[rb_id]
        if len(card["classification"]["domain"])>1:
            d1 = card["classification"]["domain"][0]
            d2 = card["classification"]["domain"][1]
        else:
            d1 = card["classification"]["domain"][0]
            d2 = None

        metadata = card.get("metadata") or {}
        attributes = card.get("attributes") or {}

        card_clean = (card["id"], card["riftbound_id"], card["name"], metadata.get("clean_name") or card["name"],
                      attributes.get("energy") or 0, attributes.get("power") or 0,
                      attributes.get("might") or 0, card["classification"]["type"],
                      card["classification"]["supertype"], card["classification"]["rarity"],
                      d1, d2, card["set"]["set_id"], card["set"]["label"],
                      card["media"]["image_url"], card["media"]["artist"],
                      metadata.get("alternate_art") or False, metadata.get("overnumbered") or False,
                      metadata.get("signature") or False)
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