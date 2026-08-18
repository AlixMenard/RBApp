from flask import Blueprint, redirect, request, session, url_for, render_template
from SQL.trades import add_trade_out, add_trade_in, get_trades_in, get_trades_out
from SQL.user_data import get_avatar_url
from collections import defaultdict
from apscheduler.schedulers.background import BackgroundScheduler

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

def find_matches():
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

            if (t:=(trade and trade_in[-1])) or (m:=(sell and trade_in[-2])):
                matches.append((card_id, user_id, trade_in[1], min(quantity, in_quantity), m, t))

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

scheduler = BackgroundScheduler()
scheduler.add_job(find_matches, 'interval', minutes=120)
scheduler.start()





