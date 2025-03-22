from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
import cv2
from pyzbar.pyzbar import decode
import MySQLdb
import pandas as pd
import joblib
from datetime import datetime
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import pdfkit
import smtplib
from email.message import EmailMessage
import os
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# MySQL Connection
db = MySQLdb.connect(host=Config.DB_HOST, user=Config.DB_USER, passwd=Config.DB_PASSWORD, db=Config.DB_NAME)
cursor = db.cursor()

# Load trained model (if exists)
try:
    model = joblib.load("model/sales_model.pkl")
except:
    model = None

@app.route("/")
def index():
    cursor.execute("SELECT * FROM inventory")
    inventory = cursor.fetchall()
    cursor.execute("SELECT * FROM transactions ORDER BY date DESC")
    transactions = cursor.fetchall()
    return render_template("index.html", inventory=inventory, transactions=transactions)

@app.route("/add", methods=["GET", "POST"])
def add_item():
    if request.method == "POST":
        item = request.form["item"]
        barcode = request.form["barcode"]
        quantity = int(request.form["quantity"])
        threshold = int(request.form.get("threshold", 0))
        cursor.execute("INSERT INTO inventory (item, barcode, quantity, threshold) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE quantity=quantity+%s", (item, barcode, quantity, threshold, quantity))
        db.commit()
        return redirect(url_for("index"))
    return render_template("add_item.html")

@app.route("/scan", methods=["GET"])
def scan_barcode():
    return render_template("scan_barcode.html")

@app.route("/sales_prediction", methods=["GET", "POST"])
def sales_prediction():
    if request.method == "POST":
        cursor.execute("SELECT quantity_sold, date FROM sales")
        sales_data = cursor.fetchall()
        if len(sales_data) < 5:
            return jsonify({"error": "Not enough data to train model"})
        df = pd.DataFrame(sales_data, columns=["quantity_sold", "date"])
        df["date"] = pd.to_datetime(df["date"])
        df["day_of_year"] = df["date"].dt.dayofyear
        X = df[["day_of_year"]]
        y = df["quantity_sold"]
        model = LinearRegression()
        model.fit(X, y)
        joblib.dump(model, "model/sales_model.pkl")
        return jsonify({"message": "Model trained successfully"})
    return render_template("sales_prediction.html")

@app.route("/generate_report", methods=["GET"])
def generate_report():
    return render_template("reports.html")

@app.route("/transactions", methods=["GET", "POST"])
def transactions():
    if request.method == "POST":
        item = request.form["item"]
        quantity = int(request.form["quantity"])
        price = float(request.form["price"])
        transaction_type = request.form["type"]
        date = datetime.now().strftime('%Y-%m-%d')
        total = quantity * price
        cursor.execute("INSERT INTO transactions (item, quantity, price, total, type, date) VALUES (%s, %s, %s, %s, %s, %s)", (item, quantity, price, total, transaction_type, date))
        db.commit()
        return redirect(url_for("transactions"))
    cursor.execute("SELECT * FROM transactions ORDER BY date DESC")
    transactions = cursor.fetchall()
    return render_template("transactions.html", transactions=transactions)

if __name__ == "__main__":
    app.run(debug=True)