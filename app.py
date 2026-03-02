import os
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine.url import make_url
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql

# -----------------------------
# APP CONFIG
# -----------------------------
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

# 🔴 CHANGE THESE VALUES
MYSQL_USER = "root"
MYSQL_PASSWORD = "jebinsam"
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_DB = "expenses_db"

DATABASE_URL = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
    f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# -----------------------------
# ENSURE DATABASE EXISTS
# -----------------------------
try:
    url = make_url(DATABASE_URL)
    conn = pymysql.connect(
        host=url.host,
        user=url.username,
        password=url.password,
        port=url.port or 3306,
        charset="utf8mb4"
    )
    with conn.cursor() as cursor:
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
        )
    conn.commit()
    conn.close()
except Exception as e:
    print("❌ Error creating database:", e)

# -----------------------------
# INIT DB
# -----------------------------
db = SQLAlchemy(app)

# -----------------------------
# MODELS
# -----------------------------
class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    expenses = db.relationship("Expense", back_populates="user", lazy=True)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Expense(db.Model):
    __tablename__ = "expense"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(100), nullable=True)
    name = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    user = db.relationship("User", back_populates="expenses")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "date": self.date,
            "category": self.category,
            "name": self.name,
            "amount": self.amount,
            "notes": self.notes,
        }


# -----------------------------
# AUTH HELPERS
# -----------------------------
def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return db.session.get(User, int(user_id))


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for("login", next=request.path))
        return fn(*args, **kwargs)

    return wrapper


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user or not user.is_admin:
            flash("Admin access required.", "error")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)

    return wrapper


@app.context_processor
def inject_current_user():
    user = get_current_user()
    return {
        "current_user": user,
        "is_admin": bool(user and user.is_admin),
    }

# -----------------------------
# CREATE TABLES
# -----------------------------
with app.app_context():
    try:
        # create tables if they don't exist (keep data between restarts)
        db.create_all()
    except Exception as e:
        print("❌ Error creating tables:", e)

# -----------------------------
# UI ROUTES
# -----------------------------
@app.route("/")
def home():
    """Public marketing / landing page."""
    return render_template("home.html")


@app.route("/dashboard")
@login_required
def dashboard():
    user = get_current_user()
    expenses = (
        Expense.query.filter_by(user_id=user.id)
        .order_by(Expense.id)
        .all()
    )
    total = sum(e.amount for e in expenses)
    return render_template(
        "index.html",
        expenses=expenses,
        total=total,
    )

@app.route("/transactions")
@app.route("/transactions/")
@login_required
def transactions():
    user = get_current_user()
    expenses = (
        Expense.query.filter_by(user_id=user.id)
        .order_by(Expense.date.desc())
        .all()
    )
    total = sum(e.amount for e in expenses)
    return render_template(
        "transactions.html",
        expenses=expenses,
        total=total
    )

@app.route("/budgets")
@app.route("/budgets/")
@login_required
def budgets():
    user = get_current_user()
    expenses = Expense.query.filter_by(user_id=user.id).all()
    category_totals = {}
    for e in expenses:
        key = e.category or "Uncategorized"
        category_totals[key] = category_totals.get(key, 0) + e.amount
    return render_template("budgets.html", category_totals=category_totals)

@app.route("/settings")
@app.route("/settings/")
@login_required
def settings():
    return render_template("settings.html")

@app.route("/profile")
@app.route("/profile/")
@login_required
def profile():
    return render_template("profile.html")

@app.route("/admin")
@app.route("/admin/")
@admin_required
def admin():
    total_expenses = db.session.query(db.func.sum(Expense.amount)).scalar() or 0
    user_count = User.query.count()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    return render_template(
        "admin.html",
        total=total_expenses,
        user_count=user_count,
        recent_users=recent_users,
    )


@app.route("/login", methods=["GET", "POST"])
@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            flash("Welcome back!", "success")
            next_url = request.args.get("next") or url_for("dashboard")
            return redirect(next_url)
        flash("Invalid email or password.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not name or not email or not password:
            flash("All fields are required.", "error")
        elif password != confirm:
            flash("Passwords do not match.", "error")
        elif User.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
        else:
            user = User(name=name, email=email)
            user.set_password(password)
            # first user becomes admin for convenience
            if User.query.count() == 0:
                user.is_admin = True
            db.session.add(user)
            db.session.commit()
            flash("Account created. You can now log in.", "success")
            return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        new_password = request.form.get("new_password", "")
        confirm = request.form.get("confirm_password", "")
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("No account found with that email.", "error")
        elif not new_password or new_password != confirm:
            flash("Passwords do not match.", "error")
        else:
            user.set_password(new_password)
            db.session.commit()
            flash("Password updated. Please log in with your new password.", "success")
            return redirect(url_for("login"))

    return render_template("forgot_password.html")

@app.route("/reports")
@app.route("/reports/")
@login_required
def reports():
    # aggregate monthly totals
    user = get_current_user()
    expenses = (
        Expense.query.filter_by(user_id=user.id)
        .order_by(Expense.date)
        .all()
    )
    totals = {}
    for e in expenses:
        month = e.date[:7]  # assumes YYYY-MM format
        totals.setdefault(month, 0)
        totals[month] += e.amount
    return render_template("reports.html", totals=totals)

@app.route("/about")
@app.route("/about/")
def about():
    return render_template("about.html")

@app.route("/add", methods=["POST"])
@login_required
def add_expense():
    # support both add and edit via form submission (fallback for non-JS)
    form_id = request.form.get("id")
    try:
        user = get_current_user()
        if form_id:
            expense = db.session.get(Expense, int(form_id))
            if expense and expense.user_id == user.id:
                expense.date = request.form["date"]
                expense.category = request.form.get("category")
                expense.name = request.form["name"]
                expense.amount = float(request.form["amount"])
                expense.notes = request.form.get("notes")
                db.session.commit()
                flash("Expense updated ✏️", "success")
            else:
                flash("Expense not found ⚠️", "error")
        else:
            expense = Expense(
                user_id=user.id,
                date=request.form["date"],
                category=request.form.get("category"),
                name=request.form["name"],
                amount=float(request.form["amount"]),
                notes=request.form.get("notes")
            )
            db.session.add(expense)
            db.session.commit()
            flash("Expense added successfully ✅", "success")
    except Exception:
        flash("Invalid input ⚠️", "error")

    return redirect(url_for("dashboard"))


@app.route("/delete/<int:id>")
@login_required
def delete_expense(id):
    user = get_current_user()
    expense = db.session.get(Expense, id)
    if expense and expense.user_id == user.id:
        db.session.delete(expense)
        db.session.commit()
        flash("Expense deleted ❌", "success")
    else:
        flash("Expense not found ⚠️", "error")

    return redirect(url_for("dashboard"))


@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_expense(id):
    user = get_current_user()
    expense = db.session.get(Expense, id)

    if not expense or expense.user_id != user.id:
        flash("Expense not found ⚠️", "error")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        try:
            expense.date = request.form["date"]
            expense.category = request.form.get("category")
            expense.name = request.form["name"]
            expense.amount = float(request.form["amount"])
            expense.notes = request.form.get("notes")
            db.session.commit()
            flash("Expense updated ✏️", "success")
            return redirect(url_for("dashboard"))
        except Exception:
            flash("Invalid input ⚠️", "error")

    expenses = (
        Expense.query.filter_by(user_id=user.id)
        .order_by(Expense.id)
        .all()
    )
    total = sum(e.amount for e in expenses)
    return render_template(
        "index.html",
        expenses=expenses,
        edit_expense=expense,
        total=total
    )

# -----------------------------
# API ROUTES (JSON)
# -----------------------------
@app.route("/api/expenses", methods=["GET"])
@login_required
def api_get_expenses():
    # support optional filtering via query params
    user = get_current_user()
    query = Expense.query.filter_by(user_id=user.id)
    start = request.args.get('start')
    end = request.args.get('end')
    cat = request.args.get('category')
    if start:
        query = query.filter(Expense.date >= start)
    if end:
        query = query.filter(Expense.date <= end)
    if cat:
        query = query.filter(Expense.category == cat)
    expenses = query.order_by(Expense.id).all()
    return jsonify([e.to_dict() for e in expenses]), 200

@app.route("/api/expenses", methods=["POST"])
@login_required
def api_add_expense():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    user = get_current_user()
    expense = Expense(
        user_id=user.id,
        date=data["date"],
        category=data.get("category"),
        name=data["name"],
        amount=float(data["amount"]),
        notes=data.get("notes")
    )
    db.session.add(expense)
    db.session.commit()

    return jsonify(expense.to_dict()), 201

@app.route("/api/expenses/<int:id>", methods=["PUT"])
@login_required
def api_update_expense(id):
    user = get_current_user()
    expense = db.session.get(Expense, id)
    if not expense or expense.user_id != user.id:
        return jsonify({"error": "Expense not found"}), 404

    data = request.get_json()
    expense.date = data.get("date", expense.date)
    expense.category = data.get("category", expense.category)
    expense.name = data.get("name", expense.name)
    if "amount" in data:
        expense.amount = float(data["amount"])
    expense.notes = data.get("notes", expense.notes)

    db.session.commit()
    return jsonify(expense.to_dict()), 200

@app.route("/api/expenses/<int:id>", methods=["DELETE"])
@login_required
def api_delete_expense(id):
    user = get_current_user()
    expense = db.session.get(Expense, id)
    if not expense or expense.user_id != user.id:
        return jsonify({"error": "Expense not found"}), 404

    db.session.delete(expense)
    db.session.commit()
    return jsonify({"message": "Expense deleted"}), 200

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)