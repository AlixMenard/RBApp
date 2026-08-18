from flask import Blueprint, redirect, request, session, url_for
from SQL.trades import get_user_trades_out, get_user_trades_in

user_trade_bp = Blueprint("user_trade", __name__)

@user_trade_bp.route("/out")
def user_trade_out():
    if not "discord_id" in session or not "user_id" in session:
        return redirect(url_for("home"))
    # id,   card_id, user_id, quantity, sell, trade
    # auto, int,     int,     int,      bool, bool
    user_id = session.get("user_id")

    result = get_user_trades_out(user_id)
    return result

@user_trade_bp.route("/in")
def user_trade_in():
    if not "discord_id" in session or not "user_id" in session:
        return redirect(url_for("home"))
    # id,   card_id, user_id, quantity, sell, trade
    # auto, int,     int,     int,      bool, bool
    user_id = session.get("user_id")

    result = get_user_trades_in(user_id)
    return result