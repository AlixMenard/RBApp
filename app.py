from flask import Flask, session, redirect, url_for, request, render_template
from SQL.user_data import get_avatar, get_id
from datetime import timedelta
import os
from dotenv import load_dotenv
import sqlite3

load_dotenv()

from Discord.OAuth import auth_bp
from trades.trade_management import trade_bp, find_matches
from trades.user_trades import user_trade_bp
from cards.card_list import update_cards

from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()
scheduler.add_job(find_matches, 'interval', minutes=120)
scheduler.start()


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)

@app.before_request
def make_session_permanent():
    session.permanent = True

@app.context_processor
def inject_user_info():
    if "discord_id" in session:
        return dict(avatar_url=get_avatar(session["discord_id"]))
    return dict(avatar_url=None)

# Register the blueprint with a prefix (e.g. /auth/login, /auth/callback)
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