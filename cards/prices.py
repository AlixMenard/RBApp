import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
import pandas as pd
from SQL.cards import get_sets, update_card_price
from cards.tcgcsv_common import BASE, CATEGORY_ID, USER_AGENT, SLEEP_BETWEEN_REQUESTS, fetch_json

def get_groups():
    data = fetch_json(f"{BASE}/tcgplayer/{CATEGORY_ID}/groups")
    return data["results"]

def get_prices(group_id):
    url = f"{BASE}/tcgplayer/{CATEGORY_ID}/{group_id}/ProductsAndPrices.csv"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        try:
            df = pd.read_csv(resp)
        except pd.errors.EmptyDataError:
            return None
    cols = ["productId" "marketPrice"]
    df = df[[c for c in cols if c in df.columns]]
    return df

def update_group_prices(group_id, set_name):
    df = get_prices(group_id)
    if df is None:
        return

    updated_count = 0
    missed = []
    for _, row in df.iterrows():
        product_id = row.get('productId')

        price = row.get('marketPrice')
        if pd.isna(price):
            continue

        rc = update_card_price(product_id, price)
        if rc:
            updated_count += 1
        else:
            missed.append(row)

    if missed:
        print(missed)

def update_prices():
    for group in get_groups():
        #print(f"Updating prices for group {group['name']}")
        time.sleep(SLEEP_BETWEEN_REQUESTS)
        update_group_prices(group["groupId"], group["name"])