import pandas as pd
import numpy as np
from datetime import datetime
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set_theme(style="whitegrid")

# 1. Load the data
url = "https://raw.githubusercontent.com/sumit0072/Superstore-Data-Analysis/main/Sample%20-%20Superstore.csv"
try:
    df = pd.read_csv(url, encoding='windows-1252')
except Exception as e:
    print(f"Error loading data: {e}")
    exit()

# 2. Data Preparation for Time Series
df['Order Date'] = pd.to_datetime(df['Order Date'])
# Resample to Monthly Sales
monthly_sales = df.set_index('Order Date')['Sales'].resample('MS').sum().to_frame()
monthly_sales.columns = ['Actual_Sales']

# 3. Model Implementation: Holt-Winters Exponential Smoothing
# This model handles both trend and seasonality, making it much more professional than a simple MA.
model = ExponentialSmoothing(
    monthly_sales['Actual_Sales'], 
    trend='add', 
    seasonal='add', 
    seasonal_periods=12
).fit()

# 4. In-Sample Predictions & Error Metrics
monthly_sales['Fitted_Values'] = model.fittedvalues
mae = mean_absolute_error(monthly_sales['Actual_Sales'], monthly_sales['Fitted_Values'])
rmse = np.sqrt(mean_squared_error(monthly_sales['Actual_Sales'], monthly_sales['Fitted_Values']))

print(f"Model Performance Metrics:")
print(f"- Mean Absolute Error (MAE): ${mae:,.2f}")
print(f"- Root Mean Squared Error (RMSE): ${rmse:,.2f}")

# 5. Forecasting the Next 6 Months
forecast_steps = 6
forecast_values = model.forecast(forecast_steps)
forecast_dates = pd.date_range(start=monthly_sales.index[-1] + pd.DateOffset(months=1), periods=forecast_steps, freq='MS')
forecast_df = pd.DataFrame({'Predicted_Sales': forecast_values}, index=forecast_dates)

# 6. Visualization
plt.figure(figsize=(12, 6))
plt.plot(monthly_sales.index, monthly_sales['Actual_Sales'], label='Historical Sales', marker='o', color='#1e3a8a')
plt.plot(monthly_sales.index, monthly_sales['Fitted_Values'], label='Fitted Model', linestyle='--', color='#10b981')
plt.plot(forecast_df.index, forecast_df['Predicted_Sales'], label='6-Month Forecast', marker='s', color='#ef4444')
plt.fill_between(forecast_df.index, forecast_df['Predicted_Sales'] * 0.9, forecast_df['Predicted_Sales'] * 1.1, color='#ef4444', alpha=0.1, label='10% Confidence Interval')

plt.title('Advanced Sales Forecasting (Holt-Winters Exponential Smoothing)', fontsize=14)
plt.ylabel('Sales ($)')
plt.legend()
plt.tight_layout()
plt.savefig('sales_forecast_advanced.png')

# 7. Save Results
monthly_sales.to_csv('Sales_Forecast_Detailed.csv')
forecast_df.to_csv('Future_Sales_Predictions_Advanced.csv')

print(f"\nAdvanced Analysis complete!")
print(f"Visual saved as 'sales_forecast_advanced.png'")
print(f"Detailed forecast saved to 'Future_Sales_Predictions_Advanced.csv'")
