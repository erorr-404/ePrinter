from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "dont_hack_me_pls"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(days=28)
# Static: {{url_for('static', filename='style.css' )}}"

db = SQLAlchemy(app)


class Users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/admin")
def admin():
    return redirect(url_for("home"))


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        email = request.form.get("eml", None)
        name = request.form.get("nm", None)
        password = request.form.get("pwd", None)

        if email and name and password:
            session.permanent = True
            session["email"] = email
            session["user"] = name
            session["password"] = password

            with app.app_context():
                if Users.query.filter_by(email=email).first():
                    flash(f"User with this email is already exists.", "error")
                else:
                    user = Users(name, email, password)
                    db.session.add(user)
                    db.session.commit()
                    flash(f"Registered successfully.", "info")

            return redirect(url_for("account"))
        else:
            flash(f"Invalid data.", "error")
    else:
        return render_template("register.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        email = request.form.get("eml", "")
        pwd = request.form.get("pwd", "")

        user = Users.query.filter_by(email=email).first()
        if user:
            if pwd == user.password:
                session["email"] = email
                session["user"] = user.name
                session["password"] = pwd
                return redirect(url_for("account"))
            else:
                flash("Invalid password", "error")
        else:
            flash("No user with this email. Register here", "error")
            return redirect(url_for("register"))

    else:
        if "user" in session:
            return redirect(url_for("account"))
        return render_template("login.html")


@app.route("/logout")
def logout():
    if "user" in session:
        user = session["user"]
        flash(f"You've been logged out, {user}!", "info")
    else:
        flash(f"You are already logged out.", "info")
    session.pop("user", None)
    session.pop("email", None)
    session.pop("password", None)
    return redirect(url_for("login"))


@app.route("/account", methods=["POST", "GET"])
def account():
    if "user" in session:
        if request.method == "POST":
            email = request.form["email"]
            session["email"] = email
            flash("Email was saved.")
        else:
            email = session.get("email", "")
        return render_template("user.html", email=email)
    else:
        return redirect(url_for("login"))


@app.route("/print")
def add_document():
    if "user" in session:
        return render_template("print.html")
    else:
        flash(f"You need to login to print.", "error")
        return redirect(url_for("login"))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run()