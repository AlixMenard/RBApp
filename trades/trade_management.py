from flask import Blueprint, redirect, request, session, url_for
from SQL.trades import add_trade_out, add_trade_in, get_trades_in, get_trades_out
from apscheduler.schedulers.background import BackgroundScheduler
from collections import defaultdict

trade_bp = Blueprint("trade", __name__)

scheduler = BackgroundScheduler()
@trade_bp.route("/out")
def trade_out():
    if not "discord_id" in session or not "user_id" in session:
        return redirect(url_for("home"))
    # id,   card_id, user_id, quantity, sell, trade
    # auto, int,     int,     int,      bool, bool
    card_id = request.args.get("card_id")
    user_id = session.get("user_id")
    quantity = request.args.get("quantity")
    sell = request.args.get("sell", True)
    trade = request.args.get("trade", True)

    add_trade_out((card_id, user_id, quantity, sell, trade))
    return "success"

@trade_bp.route("/in")
def trade_in():
    if not "discord_id" in session or not "user_id" in session:
        return redirect(url_for("home"))
    # id,   card_id, user_id, quantity, buy, trade
    # auto, int,     int,     int,      bool, bool
    card_id = request.args.get("card_id")
    user_id = session.get("user_id")
    quantity = request.args.get("quantity")
    buy = request.args.get("buy", True)
    trade = request.args.get("trade", True)

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
        card_id, user_id, quantity, sell, trade = trade_out
        if not card_id in cards_in:
            continue

        potential = cards_in[card_id]
        for trade_in in potential:
            if (t:=(trade and trade_in[-1])) or (m:=(sell and trade_in[-2])):
                matches.append((card_id, user_id, trade_in[1], min(quantity, trade_in[2]), m, t))

    return matches





scheduler.add_job(find_matches, 'interval', minutes=120)
scheduler.start()