import pandas as pd
import joblib
import numpy as np
from sklearn.linear_model import LinearRegression
import MySQLdb

# Connect to MySQL database
db = MySQLdb.connect(host="localhost", user="root", passwd="", db="inventory_db")
cursor = db.cursor()

# Fetch sales data
cursor.execute("SELECT quantity_sold, date FROM sales")
sales_data = cursor.fetchall()

if len(sales_data) < 5:
    print("❌ Not enough data to train the model.")
else:
    # Convert to DataFrame
    df = pd.DataFrame(sales_data, columns=["quantity_sold", "date"])
    df["date"] = pd.to_datetime(df["date"])
    df["day_of_year"] = df["date"].dt.dayofyear

    # Train the model
    X = df[["day_of_year"]]
    y = df["quantity_sold"]
    model = LinearRegression()
    model.fit(X, y)

    # Save the trained model
    joblib.dump(model, "model/sales_model.pkl")
    print("✅ Sales prediction model trained and saved as 'sales_model.pkl'.")

# Close database connection
db.close()
