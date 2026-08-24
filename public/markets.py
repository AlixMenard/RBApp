from flask import Blueprint, render_template
from SQL.user_data import get_avatar_url

# Create a Blueprint instead of a Flask app
public_market_bp = Blueprint("public_market", __name__)


@public_market_bp.route("/in")
def market_out():
    all_trades = get_trades_out()
    others_trades = []
    for t in all_trades:
        avatar_url = get_avatar_url(t[9], t[8])
        others_trades.append(list(t) + [avatar_url])

    return render_template("market.html",
                           trades=others_trades,
                           title="Cards available",
                           action_label="Sell")


@trade_bp.route("/market/in")
def market_in():
    all_trades = get_trades_in()
    others_trades = []
    for t in all_trades:
        avatar_url = get_avatar_url(t[9], t[8])
        others_trades.append(list(t) + [avatar_url])

    return render_template("market.html",
                           trades=others_trades,
                           title="Cards looked after",
                           action_label="Buy")