"""
SUPERSTORE BUSINESS ANALYTICS PORTFOLIO
---------------------------------------
Author: Mahis (Portfolio Implementation)
Objectives: 
1. Customer Segmentation (RFM Analysis)
2. Profitability & Discount Root-Cause Analysis
3. Sales Trend Forecasting
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Set visualization style
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

# 1. LOAD DATA
def load_and_preprocess():
    url = "https://raw.githubusercontent.com/sumit0072/Superstore-Data-Analysis/main/Sample%20-%20Superstore.csv"
    df = pd.read_csv(url, encoding='windows-1252')
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    return df

# 2. ANALYSIS 1: RFM SEGMENTATION
def perform_rfm(df):
    print("\n--- Starting RFM Analysis ---")
    snapshot_date = df['Order Date'].max() + pd.Timedelta(days=1)
    rfm = df.groupby('Customer ID').agg({
        'Order Date': lambda x: (snapshot_date - x.max()).days,
        'Order ID': 'count',
        'Sales': 'sum'
    })
    rfm.columns = ['Recency', 'Frequency', 'Monetary']
    
    # Scoring
    rfm['R'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm['F'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
    rfm['M'] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5])
    
    def segment_map(x):
        r, f = int(x['R']), int(x['F'])
        if r >= 4 and f >= 4: return 'Champions/Loyalists'
        if r >= 3 and f >= 3: return 'Potential Loyalist'
        if r <= 2 and f >= 4: return 'At Risk'
        if r <= 1: return 'Hibernating/Lost'
        return 'Recent/New'
        
    rfm['Segment'] = rfm.apply(segment_map, axis=1)
    
    # Visualization
    plt.figure(figsize=(10, 6))
    sns.countplot(data=rfm, x='Segment', palette='viridis', order=rfm['Segment'].value_counts().index)
    plt.title('Customer Segment Distribution (RFM)', fontsize=15)
    plt.savefig('rfm_segments.png')
    print("RFM Analysis Complete. Chart saved as 'rfm_segments.png'")
    return rfm

# 3. ANALYSIS 2: PROFIT & DISCOUNT IMPACT
def perform_profit_analysis(df):
    print("\n--- Starting Profitability Analysis ---")
    plt.figure(figsize=(10, 6))
    sns.regplot(data=df, x='Discount', y='Profit', scatter_kws={'alpha':0.3}, line_kws={'color':'red'})
    plt.title('Impact of Discounts on Profitability', fontsize=15)
    plt.savefig('discount_vs_profit.png')
    
    # Profit by Sub-Category
    sub_profit = df.groupby('Sub-Category')['Profit'].sum().sort_values()
    plt.figure(figsize=(12, 8))
    sns.barplot(x=sub_profit.values, y=sub_profit.index, palette='RdYlGn')
    plt.title('Profitability by Sub-Category (Identified Money Pits)', fontsize=15)
    plt.savefig('subcategory_profit.png')
    print("Profit Analysis Complete. Charts saved.")

# 4. ANALYSIS 3: SALES FORECASTING
def perform_forecasting(df):
    print("\n--- Starting Sales Forecasting ---")
    monthly = df.set_index('Order Date')['Sales'].resample('ME').sum().to_frame()
    monthly['3M_Moving_Avg'] = monthly['Sales'].rolling(window=3).mean()
    
    # Forecast 3 Months
    last_val = monthly['3M_Moving_Avg'].iloc[-1]
    forecast_idx = pd.date_range(start=monthly.index[-1] + pd.Timedelta(days=1), periods=3, freq='ME')
    forecast = pd.DataFrame({'Sales': [last_val]*3}, index=forecast_idx)
    
    # Visualization
    plt.figure(figsize=(14, 6))
    plt.plot(monthly.index, monthly['Sales'], label='Historical Sales', color='blue', marker='o')
    plt.plot(forecast.index, forecast['Sales'], label='Forecast', color='red', linestyle='--', marker='s')
    plt.title('Sales Trend & 3-Month Demand Forecast', fontsize=15)
    plt.legend()
    plt.savefig('sales_forecast.png')
    print("Forecasting Complete. Chart saved as 'sales_forecast.png'")

# MAIN EXECUTION
if __name__ == "__main__":
    data = load_and_preprocess()
    perform_rfm(data)
    perform_profit_analysis(data)
    perform_forecasting(data)
    print("\nALL ANALYTICAL COMPONENTS IMPLEMENTED SUCCESSFULLY.")
    print("Check your folder for PNG visual reports!")
