from flask import Flask, render_template, request, redirect, session, url_for
from firebase_config import db
import os
from datetime import timedelta

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "mysecret")
app.permanent_session_lifetime = timedelta(minutes=15)

# ---------------- FIREBASE FUNCTIONS ----------------
def get_user(mobile):
    ref = db.reference(f"users/{mobile}")
    return ref.get()

def is_admin(mobile):
    return mobile == "8830720742" or mobile == "9876543210"

# ---------------- ROUTES ----------------
@app.route("/", methods=["GET"])
def home():
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        mobile = request.form.get("mobile")
        password = request.form.get("password")
        user = get_user(mobile)
        if user and user.get("password") == password:
            session.permanent = True
            session['user'] = mobile
            return redirect("/admin" if is_admin(mobile) else f"/user")
        return render_template("login.html", error="Invalid mobile or password")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
