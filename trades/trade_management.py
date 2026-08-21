from flask import Blueprint, redirect, request, session, url_for, render_template, jsonify
from SQL.trades import add_trade_out, add_trade_in, get_trades_in, get_trades_out, remove_trade_in, remove_trade_out
from SQL.cards import get_cards, search_cards, get_sets
from SQL.user_data import get_avatar_url
from collections import defaultdict
from datetime import timedelta, datetime

from Discord.DM import DM
from SQL.user_data import get_discord_id, get_name

trade_bp = Blueprint("trade", __name__)

@trade_bp.route("/out")
def trade_out():
    if not "discord_id" in session or not "user_id" in session:
        return redirect(url_for("home"))
    
    card_id = request.args.get("card_id")
    user_id = session.get("user_id")
    quantity = request.args.get("quantity", 1)
    sell = request.args.get("sell", "true").lower() == "true"
    trade = request.args.get("trade", "true").lower() == "true"

    try:
        quantity = int(quantity)
    except (ValueError, TypeError):
        quantity = 0

    add_trade_out((card_id, user_id, quantity, sell, trade))
    return "success"

@trade_bp.route("/in")
def trade_in():
    if not "discord_id" in session or not "user_id" in session:
        return redirect(url_for("home"))
    
    card_id = request.args.get("card_id")
    user_id = session.get("user_id")
    quantity = request.args.get("quantity", 1)
    buy = request.args.get("buy", "true").lower() == "true"
    trade = request.args.get("trade", "true").lower() == "true"

    try:
        quantity = int(quantity)
    except (ValueError, TypeError):
        quantity = 0

    add_trade_in((card_id, user_id, quantity, buy, trade))
    return "success"

@trade_bp.route("/remove")
def remove_trade():
    if not "discord_id" in session or not "user_id" in session:
        return redirect(url_for("home"))
    
    card_id = request.args.get("card_id")
    user_id = session.get("user_id")
    trade_type = request.args.get("type")

    if trade_type == "in":
        remove_trade_in(card_id, user_id)
    elif trade_type == "out":
        remove_trade_out(card_id, user_id)
    else:
        return "error", 400
    
    return "success"

@trade_bp.route("/search")
def search_cards_route():
    args = request.args
    cards = search_cards(args)
    # Convert list of tuples to list of dicts for JSON
    card_list = []
    for card in cards:
        card_list.append({
            "id": card[0],
            "name": card[1],
            "clean_name": card[2],
            "rarity": card[3],
            "image_url": card[4],
            "domain1": card[5],
            "domain2": card[6],
            "alt": bool(card[7]),
            "ovn": bool(card[8]),
            "signed": bool(card[9]),
            "tags": card[10].split(",") if card[10] else [],
            "price": card[11],
            "set_name": card[12],
            "type": card[13]
        })
    return jsonify(card_list)

@trade_bp.route("/add")
def add_trade_page():
    if not "discord_id" in session or not "user_id" in session:
        return redirect(url_for("home"))
    
    cards = get_cards()
    sets = get_sets()
    return render_template("add_trade.html", cards=cards, sets=sets)

match_memory = {}
def find_matches():
    global match_memory
    trades_in = get_trades_in()
    trades_out = get_trades_out()
    cards_in = defaultdict(list)
    for trade in trades_in:
        cards_in[trade[0]].append(trade)

    matches = []
    for trade_out in trades_out:
        card_id, user_id, quantity, sell, trade = trade_out[:5]
        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            quantity = 0

        if not card_id in cards_in:
            continue

        potential = cards_in[card_id]
        for trade_in in potential:
            try:
                in_quantity = int(trade_in[2])
            except (ValueError, TypeError):
                in_quantity = 0

            t = trade and trade_in[-1]
            m = sell and trade_in[-2]
            if t or m:
                matches.append((card_id, user_id, trade_in[1], min(quantity, in_quantity), m, t))

    for match in matches:
        receiver, giver = match[2], match[1]
        if receiver == giver:
            continue
        receiver_id, receiver_name = get_discord_id(receiver), get_name(receiver)
        giver_id, giver_name = get_discord_id(giver), get_name(giver)

        memory_key = tuple(sorted([receiver, giver]))
        now = datetime.now()

        last_sent = match_memory.get(memory_key)
        if last_sent is None or (now - last_sent).total_seconds() > 172800:
            match_memory[memory_key] = now
            print(f"Sending DM to {receiver_name} ({receiver_id}) about {giver_name} ({giver_id})")
            DM(giver_id, giver_name, receiver_id, receiver_name)

    return matches

@trade_bp.route("/market/out")
def market_out():
    if not "discord_id" in session or not "user_id" in session:
        return redirect(url_for("home"))
    
    current_user_id = session.get("user_id")
    all_trades = get_trades_out()
    # Filter to show only others' trades
    others_trades = []
    for t in all_trades:
        if t[1] != current_user_id:
            # t[7] is avatar hash, t[8] is discord_id
            avatar_url = get_avatar_url(t[9], t[8])
            others_trades.append(list(t) + [avatar_url])
    
    return render_template("market.html", 
                           trades=others_trades, 
                           title="Cards Others Are Selling", 
                           action_label="Sell")

@trade_bp.route("/market/in")
def market_in():
    if not "discord_id" in session or not "user_id" in session:
        return redirect(url_for("home"))
    
    current_user_id = session.get("user_id")
    all_trades = get_trades_in()
    # Filter to show only others' trades
    others_trades = []
    for t in all_trades:
        if t[1] != current_user_id:
            avatar_url = get_avatar_url(t[9], t[8])
            others_trades.append(list(t) + [avatar_url])
    
    return render_template("market.html", 
                           trades=others_trades, 
                           title="Cards Others Want", 
                           action_label="Buy")





