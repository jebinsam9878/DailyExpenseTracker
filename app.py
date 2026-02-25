import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine.url import make_url
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
# MODEL
# -----------------------------
class Expense(db.Model):
    __tablename__ = "expense"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date,
            "name": self.name,
            "amount": self.amount
        }

# -----------------------------
# CREATE TABLES
# -----------------------------
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print("❌ Error creating tables:", e)

# -----------------------------
# UI ROUTES
# -----------------------------
@app.route("/")
def index():
    expenses = Expense.query.order_by(Expense.id).all()
    total = sum(e.amount for e in expenses)
    return render_template(
        "index.html",
        expenses=expenses,
        total=total
    )

@app.route("/add", methods=["POST"])
def add_expense():
    try:
        expense = Expense(
            date=request.form["date"],
            name=request.form["name"],
            amount=float(request.form["amount"])
        )
        db.session.add(expense)
        db.session.commit()
        flash("Expense added successfully ✅", "success")
    except Exception:
        flash("Invalid input ⚠️", "error")

    return redirect(url_for("index"))

@app.route("/delete/<int:id>")
def delete_expense(id):
    expense = db.session.get(Expense, id)
    if expense:
        db.session.delete(expense)
        db.session.commit()
        flash("Expense deleted ❌", "success")
    else:
        flash("Expense not found ⚠️", "error")

    return redirect(url_for("index"))

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_expense(id):
    expense = db.session.get(Expense, id)

    if not expense:
        flash("Expense not found ⚠️", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        try:
            expense.date = request.form["date"]
            expense.name = request.form["name"]
            expense.amount = float(request.form["amount"])
            db.session.commit()
            flash("Expense updated ✏️", "success")
            return redirect(url_for("index"))
        except Exception:
            flash("Invalid input ⚠️", "error")

    expenses = Expense.query.order_by(Expense.id).all()
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
def api_get_expenses():
    expenses = Expense.query.order_by(Expense.id).all()
    return jsonify([e.to_dict() for e in expenses]), 200

@app.route("/api/expenses", methods=["POST"])
def api_add_expense():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    expense = Expense(
        date=data["date"],
        name=data["name"],
        amount=float(data["amount"])
    )
    db.session.add(expense)
    db.session.commit()

    return jsonify(expense.to_dict()), 201

@app.route("/api/expenses/<int:id>", methods=["PUT"])
def api_update_expense(id):
    expense = db.session.get(Expense, id)
    if not expense:
        return jsonify({"error": "Expense not found"}), 404

    data = request.get_json()
    expense.date = data.get("date", expense.date)
    expense.name = data.get("name", expense.name)
    if "amount" in data:
        expense.amount = float(data["amount"])

    db.session.commit()
    return jsonify(expense.to_dict()), 200

@app.route("/api/expenses/<int:id>", methods=["DELETE"])
def api_delete_expense(id):
    expense = db.session.get(Expense, id)
    if not expense:
        return jsonify({"error": "Expense not found"}), 404

    db.session.delete(expense)
    db.session.commit()
    return jsonify({"message": "Expense deleted"}), 200

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)