import requests
from tqdm import tqdm

base_url = "https://api.riftcodex.com"

def get_cards():

    print("Fetching cards...", end=" ", flush=True)

    page_number = 1
    page_size = 100

    url = "/cards"
    sort = "collector_number"
    dir = 1

    all_cards = []

    with tqdm() as pbar:
        while True:
            full_url = f"{base_url}{url}?sort={sort}&dir={dir}&page={page_number}&size={page_size}"
            response = requests.get(full_url)
            response.raise_for_status()  # Check for HTTP errors

            data = response.json()

            # Adjust 'data' if the list is wrapped in a key, e.g., data["results"]
            cards = data["items"]

            if not cards:
                break

            all_cards.extend(cards)
            page_number += 1
            pbar.update(len(cards))

    print("Done;")
    return all_cards