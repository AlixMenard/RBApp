import sqlite3
from flask import Blueprint, redirect, request, session, url_for
import requests
from dotenv import load_dotenv
import os
from SQL.user_data import save_or_update_user, change_dm_status

load_dotenv()

# Create a Blueprint instead of a Flask app
auth_bp = Blueprint("auth", __name__)

DISCORD_CLIENT_ID = os.getenv("DS_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.getenv("DS_CLIENT_SECRET")
DISCORD_REDIRECT_URI = " https://freedom-daunting-petted.ngrok-free.dev/auth/callback"
DISCORD_API_URL = "https://discord.com/api/v10"


@auth_bp.route("/login")
def login():
    if "discord_id" in session:
        return redirect(url_for("home"))
    auth_url = (
        f"{DISCORD_API_URL}/oauth2/authorize"
        f"?client_id={DISCORD_CLIENT_ID}"
        f"&redirect_uri={DISCORD_REDIRECT_URI}"
        f"&response_type=code&scope=identify"
    )
    return redirect(auth_url)


@auth_bp.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Authorization failed.", 400

    token_res = requests.post(
        f"{DISCORD_API_URL}/oauth2/token",
        data={
            "client_id": DISCORD_CLIENT_ID,
            "client_secret": DISCORD_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": DISCORD_REDIRECT_URI,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    access_token = token_res.json().get("access_token")
    user_res = requests.get(
        f"{DISCORD_API_URL}/users/@me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    user_data = user_res.json()

    save_or_update_user(user_data)
    session.permanent = True
    session["discord_id"] = user_data["id"]
    session["discord_name"] = user_data["username"]

    return redirect(url_for("home"))

@auth_bp.route("/dm_status")
def dm_status():
    if "discord_id" not in session or "user_id" not in session:
        return redirect(url_for("home"))

    status = requests.args.get("status")
    change_dm_status(session["user_id"], status)