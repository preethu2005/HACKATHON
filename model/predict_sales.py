import joblib
import numpy as np

# Load the trained model
model = joblib.load("model/sales_model.pkl")

# Predict sales for a future day (e.g., Day 35)
future_day = np.array([[35]])  # Example future date
predicted_sales = model.predict(future_day)

print(f"📊 Predicted Sales for Day {future_day[0][0]}: {predicted_sales[0]:.2f} units")
