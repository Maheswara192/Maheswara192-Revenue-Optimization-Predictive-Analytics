import pandas as pd
import numpy as np
from datetime import datetime

# 1. Load the data
url = "https://raw.githubusercontent.com/sumit0072/Superstore-Data-Analysis/main/Sample%20-%20Superstore.csv"
try:
    df = pd.read_csv(url, encoding='windows-1252')
except Exception as e:
    print(f"Error loading data: {e}")
    exit()

# 2. Data Preparation for Time Series
df['Order Date'] = pd.to_datetime(df['Order Date'])
# Set Order Date as index
df.set_index('Order Date', inplace=True)

# 3. Resample to Monthly Sales
# This summarizes sales into month-end buckets
monthly_sales = df['Sales'].resample('ME').sum().to_frame()
monthly_sales.columns = ['Actual_Sales']

print(f"Time Range: {monthly_sales.index.min().date()} to {monthly_sales.index.max().date()}")
print("\nLast 6 months of historical sales:")
print(monthly_sales.tail(6))

# 4. Simple Predictive Model: 3-Month Moving Average
# This is a standard baseline for inventory planning
monthly_sales['Moving_Avg_3M'] = monthly_sales['Actual_Sales'].rolling(window=3).mean()

# 5. Forecasting the Next 3 Months
# We'll take the latest trend and extend it
last_date = monthly_sales.index.max()
forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=3, freq='ME')

# Use the last calculated moving average as the prediction for the next 3 months
last_ma = monthly_sales['Moving_Avg_3M'].iloc[-1]
forecast_df = pd.DataFrame({'Predicted_Sales': [last_ma] * 3}, index=forecast_dates)

print("\n--- Sales Forecast for Next 3 Months ---")
print(forecast_df)

# 6. Combined View and Save
# Identify Year and Month for easy reading
monthly_sales['Year'] = monthly_sales.index.year
monthly_sales['Month'] = monthly_sales.index.month

output_path = 'Sales_Forecast_Results.csv'
monthly_sales.to_csv(output_path)
forecast_df.to_csv('Future_Sales_Predictions.csv')

print(f"\nAnalysis complete!")
print(f"Historical data saved to '{output_path}'")
print(f"Future predictions saved to 'Future_Sales_Predictions.csv'")
