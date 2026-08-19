import json
import urllib.request

BASE = "https://tcgcsv.com"
CATEGORY_ID = 89  # Riftbound: League of Legends Trading Card Game
USER_AGENT = "RiftboundPriceTracker/1.0"  # TCGCSV asks for a descriptive UA
SLEEP_BETWEEN_REQUESTS = 0.15  # be polite, per TCGCSV's usage guidelines


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))