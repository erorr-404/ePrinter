import os
from datetime import datetime
from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'files'  # Configure upload folder

app = Flask(__name__)
app.secret_key = "dont_hack_me_pls"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(days=28)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Static: {{url_for('static', filename='style.css' )}}"

db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password


class Files(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Link to User
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)  # Actual path where the file is stored
    upload_date = db.Column(db.DateTime, default=datetime.now())
    file_type = db.Column(db.String(50))  # e.g., "image/png"

    def __init__(self, user_id, file_name: str, file_path=f"{app.config['UPLOAD_FOLDER']}/"):
        self.user_id = user_id
        self.filename = file_name
        self.filepath = file_path
        self.file_type = file_name.split(".")[1]


class FilePart(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'), nullable=False)
    part_number = db.Column(db.Integer, nullable=False)  # Part order
    part_filepath = db.Column(db.String(255), nullable=False)  # Path to a part

    def __init__(self, file_id, file_name, part_number):
        self.file_id = file_id
        self.part_number = part_number
        self.part_filepath = f"{file_name}_part_{part_number}"


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


@app.route("/print", methods=["POST", "GET"])
def add_document():
    if request.method == "GET":
        if "user" in session:
            return render_template("print.html")
        else:
            flash(f"You need to login to print.", "error")
            return redirect(url_for("login"))
    else:
        if "file" not in request.files or request.files["file"] == ("" or " "):
            flash("File field can't be empty", "error")
            return redirect(url_for("add_document"))
        else:
            user = Users.query.filter_by(name=session.get("user", "")).first()
            if user:
                file = request.files["file"]
                file_name = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
                # self, user_id, file_name: str, file_path=f"{app.config['UPLOAD_FOLDER']}/"
                db_file = Files(user_id=user.id, file_name=file_name)
                db.session.add(db_file)
                db.session.commit()
                file.save(file_path)

                flash("File have been added", "success")
                return redirect(url_for("account"))
            else:
                flash("Error: no such user", "error")
                return redirect(url_for("add_document"))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run()