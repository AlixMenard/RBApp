import re
import time

from tqdm import tqdm

from cards.tcgcsv_common import BASE, CATEGORY_ID, SLEEP_BETWEEN_REQUESTS, fetch_json

TYPE_MODIFIERS = {"Champion", "Signature", "Token"}


def split_type_and_supertype(raw_card_type):
    if not raw_card_type:
        return None, None

    parts = re.split(r"[;\s]+", raw_card_type.strip())
    modifiers = [p for p in parts if p in TYPE_MODIFIERS]
    base = [p for p in parts if p not in TYPE_MODIFIERS]

    card_type = base[0] if base else raw_card_type
    supertype = modifiers[0] if modifiers else None
    return card_type, supertype


def parse_domains(raw_domain):
    if not raw_domain or raw_domain == "None":
        return ["None"]
    return raw_domain.split(";")


def parse_stat(raw_value):
    if raw_value is None:
        return 0
    first = str(raw_value).split("//")[0].strip()
    try:
        return int(float(first))
    except (TypeError, ValueError):
        return 0


def _extended_data(product):
    return {item["name"]: item["value"] for item in (product.get("extendedData") or [])}


def _build_card(product, group):
    ext = _extended_data(product)

    number = ext.get("Number") or ext.get("Card Number")
    card_type_raw = ext.get("Card Type") or ext.get("Type")
    rarity = ext.get("Rarity")

    if not card_type_raw and "Alternate Art" in product["name"]:
        card_type_raw = "Champion Unit"

    if not number or not card_type_raw:
        return None

    name = product["name"]
    card_type, supertype = split_type_and_supertype(card_type_raw)

    alternate_art = "(Alternate Art)" in name
    signature = "(Signature)" in name
    overnumbered = "(Overnumbered)" in name or signature

    set_code = group.get("abbreviation") or str(group["groupId"])
    riftbound_id = f"{set_code}-{number.replace('/', '-')}"

    return {
        "id": str(product["productId"]),
        "riftbound_id": riftbound_id,
        "name": name,
        "metadata": {
            "updated_on": product.get("modifiedOn"),
            "clean_name": product.get("cleanName"),
            "alternate_art": alternate_art,
            "overnumbered": overnumbered,
            "signature": signature,
        },
        "attributes": {
            "energy": parse_stat(ext.get("Energy Cost") or ext.get("EnergyCost")),
            "power": parse_stat(ext.get("Power Cost") or ext.get("PowerCost")),
            "might": parse_stat(ext.get("Might")),
        },
        "classification": {
            "domain": parse_domains(ext.get("Domain")),
            "type": card_type,
            "supertype": supertype,
            "rarity": rarity,
        },
        "set": {
            "set_id": set_code,
            "label": group["name"],
        },
        "media": {
            "image_url": product.get("imageUrl"),
        },
        "tags": [],
    }


def get_cards():
    print("Fetching cards...", end=" ", flush=True)

    groups = fetch_json(f"{BASE}/tcgplayer/{CATEGORY_ID}/groups")["results"]

    all_cards = []
    with tqdm(groups) as pbar:
        for group in pbar:
            time.sleep(SLEEP_BETWEEN_REQUESTS)
            products = fetch_json(f"{BASE}/tcgplayer/{CATEGORY_ID}/{group['groupId']}/products")["results"]
            for product in products:
                card = _build_card(product, group)
                if card is not None:
                    all_cards.append(card)

    print("Done;", len(all_cards))
    return all_cards