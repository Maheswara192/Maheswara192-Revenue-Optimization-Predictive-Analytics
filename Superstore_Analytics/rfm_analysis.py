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

# 2. Data Preparation
# Convert Order Date to datetime objects
df['Order Date'] = pd.to_datetime(df['Order Date'])

# We define "Today" as one day after the most recent purchase in the dataset for analysis
snapshot_date = df['Order Date'].max() + pd.Timedelta(days=1)

print(f"Analysis Snapshot Date: {snapshot_date.date()}")

# 3. Calculate RFM Metrics
rfm = df.groupby('Customer ID').agg({
    'Order Date': lambda x: (snapshot_date - x.max()).days, # Recency
    'Order ID': 'count',                                   # Frequency
    'Sales': 'sum'                                         # Monetary
})

# Rename columns for clarity
rfm.rename(columns={
    'Order Date': 'Recency',
    'Order ID': 'Frequency',
    'Sales': 'Monetary'
}, inplace=True)

print("\nFirst 5 rows of calculated metrics:")
print(rfm.head())

# 4. Scoring (Quintiles 1-5)
# R_Score: Low recency (recent purchase) is GOOD -> Score 5
# F_Score: High frequency is GOOD -> Score 5
# M_Score: High monetary is GOOD -> Score 5

rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1])
rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
rfm['M_Score'] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5])

# Create a combined RFM Score
rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)

# 5. Define Customer Segments
def segment_customer(df):
    r = int(df['R_Score'])
    f = int(df['F_Score'])
    m = int(df['M_Score'])
    
    if r >= 4 and f >= 4 and m >= 4:
        return 'VIP / Champions'
    elif r >= 4 and f >= 2:
        return 'Loyal Customers'
    elif r >= 3 and f >= 3:
        return 'Potential Loyalist'
    elif r <= 2 and f >= 4:
        return 'At Risk'
    elif r <= 1:
        return 'Lost / Hibernating'
    else:
        return 'Others/Standard'

rfm['Segment'] = rfm.apply(segment_customer, axis=1)

# 6. Summary and Save
print("\nSegment Distribution:")
print(rfm['Segment'].value_counts())

output_path = 'Superstore_RFM_Analysis.csv'
rfm.to_csv(output_path)
print(f"\nAnalysis complete! Results saved to '{output_path}'")
