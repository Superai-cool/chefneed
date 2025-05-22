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

def get_all_users():
    return db.reference("users").get() or {}

def add_or_update_user(data):
    db.reference(f"users/{data['mobile']}").set(data)

def delete_user(mobile):
    db.reference(f"users/{mobile}").delete()

def get_all_chefs():
    return db.reference("chefs").get() or {}

def get_chef(chef_id):
    return db.reference(f"chefs/{chef_id}").get()

def add_or_update_chef(chef_id, data):
    db.reference(f"chefs/{chef_id}").set(data)

def delete_chef(chef_id):
    db.reference(f"chefs/{chef_id}").delete()

def unlock_for_user(mobile, chef_id):
    ref = db.reference(f"unlocks/{mobile}/{chef_id}")
    ref.set(True)

def is_unlocked(mobile, chef_id):
    return db.reference(f"unlocks/{mobile}/{chef_id}").get() == True

def is_admin(mobile):
    return mobile in ["8830720742", "9876543210"]

# ---------------- ROUTES ----------------
@app.route("/")
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
            return redirect("/admin" if is_admin(mobile) else "/user")
        return render_template("login.html", error="Invalid mobile or password")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect("/login")

@app.route("/user")
def user_dashboard():
    if 'user' not in session: return redirect("/login")
    mobile = session['user']
    user = get_user(mobile)
    chefs = get_all_chefs()
    for cid, chef in chefs.items():
        chef['id'] = cid
        chef['unlocked'] = is_unlocked(mobile, cid)
    return render_template("user_dashboard.html", user=user, chefs=chefs.values())

@app.route("/unlock/<chef_id>", methods=["POST"])
def unlock_chef(chef_id):
    if 'user' not in session: return redirect("/login")
    mobile = session['user']
    user = get_user(mobile)
    if not is_unlocked(mobile, chef_id) and int(user.get("credits", 0)) > 0:
        db.reference(f"users/{mobile}/credits").set(int(user['credits']) - 1)
        unlock_for_user(mobile, chef_id)
    return redirect("/user")

@app.route("/admin")
def admin_dashboard():
    if 'user' not in session or not is_admin(session['user']): return redirect("/login")
    return render_template("admin_dashboard.html", users=get_all_users(), chefs=get_all_chefs())

@app.route("/admin/users", methods=["POST"])
def admin_add_user():
    if 'user' not in session or not is_admin(session['user']): return redirect("/login")
    data = {
        "mobile": request.form["mobile"],
        "name": request.form["name"],
        "password": request.form["password"],
        "credits": int(request.form["credits"])
    }
    add_or_update_user(data)
    return redirect("/admin")

@app.route("/admin/delete_user/<mobile>", methods=["POST"])
def admin_delete_user(mobile):
    if 'user' not in session or not is_admin(session['user']): return redirect("/login")
    delete_user(mobile)
    return redirect("/admin")

@app.route("/admin/chefs", methods=["POST"])
def admin_add_chef():
    if 'user' not in session or not is_admin(session['user']): return redirect("/login")
    cid = request.form["id"]
    data = {
        "name": request.form["name"],
        "cuisine": request.form["cuisine"],
        "city": request.form["city"],
        "language": request.form["language"],
        "experience": request.form["experience"],
        "desc": request.form["desc"],
        "wa": request.form["wa"]
    }
    add_or_update_chef(cid, data)
    return redirect("/admin")

@app.route("/admin/delete_chef/<cid>", methods=["POST"])
def admin_delete_chef(cid):
    if 'user' not in session or not is_admin(session['user']): return redirect("/login")
    delete_chef(cid)
    return redirect("/admin")

if __name__ == "__main__":
    app.run(debug=True)
