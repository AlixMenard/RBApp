from Discord.OAuth import auth_bp
from flask import Flask, session
from SQL.user_data import get_avatar
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)

@app.before_request
def make_session_permanent():
    session.permanent = True

# Register the blueprint with a prefix (e.g. /auth/login, /auth/callback)
app.register_blueprint(auth_bp, url_prefix="/auth")


@app.route("/")
def home():
    if "discord_id" in session:
        avatar_url = get_avatar(session["discord_id"])
        return f'''
            <h1>Welcome, {session["discord_name"]}</h1>
            <img src="{avatar_url}" width="100" height="100" style="border-radius: 50%;" alt="Profile Avatar" />
        '''
    return '<a href="/auth/login">Log in with Discord</a>'


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)