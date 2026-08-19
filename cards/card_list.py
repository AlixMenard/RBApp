from cards.tcgcsv_cards import get_cards
from SQL.tables import delete_table
from SQL.cards import add_cards, add_tags
from database.creation.cards import init_cards

from tqdm import tqdm
from collections import Counter

def update_cards():

    delete_table("cards")
    init_cards()

    all_cards = get_cards()

    # Deduplicate cards sharing the same riftbound_id, keeping the most recently updated one
    latest_cards = {}
    for card in all_cards:
        rbid = card["riftbound_id"]
        updated_on = (card.get("metadata") or {}).get("updated_on")

        existing = latest_cards.get(rbid)
        if existing is None:
            latest_cards[rbid] = card
            continue

        existing_updated_on = (existing.get("metadata") or {}).get("updated_on")

        # Keep whichever has a later updated_on; cards missing the field lose to any that have it
        if updated_on and (not existing_updated_on or updated_on > existing_updated_on):
            latest_cards[rbid] = card

    all_cards = list(latest_cards.values())

    all_cards_clean = []
    for card in tqdm(all_cards):
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
                      card["media"]["image_url"], metadata.get("alternate_art") or False,
                      (metadata.get("overnumbered") or False) or (metadata.get("signature") or False),
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

    # Sanity check: should print nothing now that duplicates are deduped above
    rbids = [card[0][1] for card in all_cards_clean]
    counts = Counter(rbids)
    for rbid, count in counts.items():
        if count > 1:
            print(rbid, count)

    add_cards(all_cards_clean)