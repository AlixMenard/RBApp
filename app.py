from flask import Flask, session, redirect, url_for, request, render_template, send_from_directory
from SQL.user_data import get_avatar, get_id, get_avatar_url, get_dm_status
from SQL.matches import get_user_matches
from datetime import timedelta
import os
from dotenv import load_dotenv
import sqlite3

load_dotenv()

from Discord.OAuth import auth_bp
from Discord.DM import DM
from trades.trade_management import trade_bp, find_matches
from trades.user_trades import user_trade_bp
from cards.card_list import update_cards
from cards.prices import update_prices

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
scheduler = BackgroundScheduler()

cards_trigger = CronTrigger(day_of_week="mon", hour="2", minute="0", second="0")
prices_trigger = CronTrigger(year="*", month="*", day="*", hour="3", minute="0", second="0")
scheduler.add_job(find_matches, 'interval', minutes=5)
scheduler.add_job(update_cards, trigger=cards_trigger)
scheduler.add_job(update_prices, trigger=prices_trigger)

scheduler.start()


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory('assets', filename)

@app.before_request
def make_session_permanent():
    session.permanent = True
    if "discord_id" in session:
        current_id = get_id(session["discord_id"])
        if current_id is None:
            session.clear()
        else:
            session["user_id"] = current_id  # always resync, don't trust a cached value

@app.context_processor
def inject_user_info():
    if "discord_id" in session:
        user_id = session.get("user_id")
        discord_id = session["discord_id"]
        if user_id is None:
            user_id = get_id(session["discord_id"])
            session["user_id"] = user_id
        return dict(
            avatar_url=get_avatar(session["discord_id"]),
            dm_status=get_dm_status(discord_id) if discord_id else False,
        )
    return dict(avatar_url=None, dm_status=False)



app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(trade_bp, url_prefix="/trade")
app.register_blueprint(user_trade_bp, url_prefix="/user_trade")



@app.route("/")
def home():
    if "discord_id" in session:
        if not "user_id" in session:
            session["user_id"] = get_id(session["discord_id"])

        avatar_url = get_avatar(session["discord_id"])
        return render_template("home.html", avatar_url=avatar_url)
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/matches")
def matches():
    if "discord_id" not in session or "user_id" not in session:
        return redirect(url_for("home"))

    user_id = session.get("user_id")
    raw_matches = get_user_matches(user_id)

    giving = []
    receiving = []
    for row in raw_matches:
        (card_id, giver_id, receiver_id, quantity, money, trade,
         card_name, image_url,
         giver_username, giver_avatar_hash, giver_discord_id,
         receiver_username, receiver_avatar_hash, receiver_discord_id) = row

        entry = {
            "card_id": card_id,
            "card_name": card_name,
            "image_url": image_url,
            "quantity": quantity,
            "money": bool(money),
            "trade": bool(trade),
            "giver_username": giver_username,
            "giver_avatar": get_avatar_url(giver_discord_id, giver_avatar_hash),
            "receiver_username": receiver_username,
            "receiver_avatar": get_avatar_url(receiver_discord_id, receiver_avatar_hash),
        }

        if giver_id == user_id:
            giving.append(entry)
        if receiver_id == user_id:
            receiving.append(entry)

    return render_template("matches.html", giving=giving, receiving=receiving)

@app.route("/admin/updatecards")
def updatecards():
    pw = request.args.get("password")
    if pw is None or pw != os.getenv("ADMIN_PASSWORD"):
        return
    update_cards()

@app.route("/admin/updatematches")
def updatematches():
    return find_matches()

@app.route("/show")
def show():
    table = request.args.get("table")
    conn = sqlite3.connect("database/app.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table}")
    result = cursor.fetchall()
    conn.commit()
    conn.close()
    return result

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)